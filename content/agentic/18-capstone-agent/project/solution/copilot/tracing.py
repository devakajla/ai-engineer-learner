"""Tracing and agent evals: a list of spans per request, a trajectory check, and a regression gate."""

import json
import math
import time

from copilot.embed import embed_texts
from copilot.llm import DEFAULT_MODEL
from copilot.rag import build_rag_messages, retrieve


def add_span(trace, name, kind, start, end, **attrs):
    """Add one record to the trace. kind is "llm" or "tool". Times are in seconds, ms is rounded."""
    span = {"name": name, "kind": kind, "ms": round((end - start) * 1000), **attrs}
    trace.append(span)
    return span


def traced_call(trace, name, kind, clock, fn, *args, **kwargs):
    """Run fn and record a span. A failure is recorded too, then raised again."""
    start = clock()
    try:
        result = fn(*args, **kwargs)
    except Exception as error:
        add_span(trace, name, kind, start, clock(), error=str(error))
        raise
    add_span(trace, name, kind, start, clock())
    return result


def trace_summary(trace):
    return {
        "spans": len(trace),
        "total_ms": sum(s["ms"] for s in trace),
        "llm_calls": sum(1 for s in trace if s["kind"] == "llm"),
        "tool_calls": sum(1 for s in trace if s["kind"] == "tool"),
        "tokens": sum(s.get("tokens", 0) for s in trace),
        "errors": sum(1 for s in trace if s.get("error")),
    }


def tool_names(trace):
    return [span["name"] for span in trace if span["kind"] == "tool"]


def trajectory_match(actual, expected, mode="exact"):
    """Compare the tools that were used with the tools we expected. Modes: exact, in_order, any_order."""
    if mode == "exact":
        return actual == expected
    if mode == "in_order":
        remaining = iter(actual)
        return all(name in remaining for name in expected)
    if mode == "any_order":
        return all(name in actual for name in expected)
    raise ValueError(f"unknown mode: {mode}")


def llm_call(client, messages, model=DEFAULT_MODEL):
    """One model call that also reports the tokens used (0 when the response has no usage)."""
    response = client.chat.completions.create(model=model, messages=messages, temperature=0)
    usage = getattr(response, "usage", None)
    tokens = getattr(usage, "total_tokens", 0) or 0
    return response.choices[0].message.content, tokens


def traced_rag(client, collection, question, clock=time.perf_counter, k=3, embed=embed_texts, model=DEFAULT_MODEL):
    """RAG with a span for the search and a span for the model call (with its tokens).

    Returns {"answer", "hits", "trace"}.
    """
    trace = []
    hits = traced_call(trace, "retrieve", "tool", clock, retrieve, collection, question, k=k, embed=embed)
    messages = build_rag_messages(question, hits)
    start = clock()
    text, tokens = llm_call(client, messages, model)
    add_span(trace, "answer", "llm", start, clock(), tokens=tokens)
    return {"answer": text, "hits": hits, "trace": trace}


def pass_rate(results):
    if not results:
        return 0.0
    return round(sum(1 for r in results if r["passed"]) / len(results), 2)


def run_eval(agent, cases, mode="in_order"):
    """Run every case. agent(input) gives {"answer", "trace"}. A crash is a failed case, not a crashed eval."""
    results = []
    for case in cases:
        try:
            out = agent(case["input"])
        except Exception as error:
            results.append({"id": case["id"], "answer_ok": False, "trajectory_ok": False, "passed": False,
                            "steps": 0, "tokens": 0, "ms": 0, "error": str(error)})
            continue
        answer = out["answer"].lower()
        answer_ok = all(word.lower() in answer for word in case.get("must_contain", []))
        used = tool_names(out["trace"])
        trajectory_ok = trajectory_match(used, case.get("expected_tools", []), mode)
        summary = trace_summary(out["trace"])
        results.append({"id": case["id"], "answer_ok": answer_ok, "trajectory_ok": trajectory_ok,
                        "passed": answer_ok and trajectory_ok, "steps": len(used),
                        "tokens": summary["tokens"], "ms": summary["total_ms"]})
    return results


def find_regressions(baseline, new):
    """Ids of cases that passed in the baseline and fail now."""
    before = {r["id"]: r["passed"] for r in baseline}
    return [r["id"] for r in new if before.get(r["id"]) and not r["passed"]]


def gate(baseline, new, max_drop=0.05, max_token_growth=0.2):
    """Block a change that lowers the pass rate, breaks a passing case, or makes the run much more expensive."""
    reasons = []
    drop = round(pass_rate(baseline) - pass_rate(new), 2)
    if drop > max_drop:
        reasons.append(f"pass rate fell by {drop}")
    regressions = find_regressions(baseline, new)
    if regressions:
        reasons.append("regressions: " + ", ".join(regressions))
    old_tokens = sum(r["tokens"] for r in baseline)
    new_tokens = sum(r["tokens"] for r in new)
    if old_tokens and (new_tokens - old_tokens) / old_tokens > max_token_growth:
        reasons.append(f"token use grew by {round(100 * (new_tokens - old_tokens) / old_tokens)}%")
    return {"ok": not reasons, "reasons": reasons}


def load_json(path):
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def percentile(values, p):
    """Nearest-rank percentile. [] gives 0."""
    if not values:
        return 0
    ordered = sorted(values)
    rank = math.ceil(p / 100 * len(ordered))
    return ordered[max(rank, 1) - 1]
