# Step 23 — Trace every request and gate every change

You cannot improve what you cannot see. This step adds two things from agentic lesson 16: **tracing** (one record per step of a request) and **agent evals** (a fixed set of cases, run on every change, with a gate that blocks a change that makes Copilot worse).

Your folder after this step (new files marked):

```
devdocs-copilot/
├── evals/
│   └── agent_cases.json    <- new (copy agent_cases.example.json and write your own cases)
└── copilot/
    ├── tracing.py          <- new
    ├── trace_cli.py        <- new
    └── ... (all files from step 22)
```

### 1. `copilot/tracing.py`

```python
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
```

Read it in parts:

1. **A span** is one record: a name, a `kind` (`"llm"` or `"tool"`), the time in milliseconds, and extra facts (`tokens`, `error`). A **trace** is the list of spans of one request. `add_span` takes start and end in **seconds** and stores milliseconds. You pass the clock in, so tests can use a fake one and need no sleeping.
2. **`traced_call`** wraps any function. It records a span after the call. If the function raises, it records the span **with the error**, then raises the error again. Tracing must never hide a failure and never cause one.
3. **`trace_summary`** adds the spans up: how many model calls, tool calls, tokens and errors, and the total time. This is the line you read first when a request was slow or expensive.
4. **Trajectory** means *which tools were used, and in what order*. `trajectory_match` has three modes: `exact` (the same list), `in_order` (the expected tools appear in this order, others may be in between), `any_order` (all of them were used). Most agent checks use `in_order`: strict enough to catch a wrong path, loose enough to allow a harmless extra step.
5. **`llm_call`** returns the text **and** the tokens (`usage.total_tokens`). A response without usage counts as 0 tokens, so a missing field never crashes tracing.
6. **`traced_rag`** is Copilot with tracing: one `tool` span for the search (`retrieve`) and one `llm` span for the answer, with its tokens. It returns the answer, the hits and the trace.
7. **`run_eval`** runs every case through `agent(input)`. For each case it checks the **answer** (every word in `must_contain` appears, ignoring case) and the **trajectory** (the tools used against `expected_tools`). Both must be true for a pass. If the agent **crashes**, that case fails with the error text. One bad case must not stop the whole eval.
8. **`gate`** compares a new run with the baseline. It blocks when: the pass rate fell by more than `max_drop`, **any** case that passed before fails now (a regression, even if the average is fine), or the tokens grew by more than 20%. The reasons are listed, so a failed gate tells you what to look at.

### 2. Run it: `copilot/trace_cli.py`

```python
"""Trace one question, or run an agent eval and compare it with a baseline. Usage:

    python -m copilot.trace_cli ask "how do I delete a task"
    python -m copilot.trace_cli eval evals/agent_cases.json              # prints the results
    python -m copilot.trace_cli eval evals/agent_cases.json baseline.json  # also runs the gate
"""

import json
import sys

from copilot.llm import get_client
from copilot.store import open_collection
from copilot.tracing import gate, load_json, pass_rate, percentile, run_eval, trace_summary, traced_rag

DB_PATH = ".chroma"


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return
    client = get_client()
    collection = open_collection(DB_PATH)
    if sys.argv[1] == "ask":
        out = traced_rag(client, collection, " ".join(sys.argv[2:]))
        for span in out["trace"]:
            print(span)
        print(trace_summary(out["trace"]))
        print(out["answer"])
        return
    cases = load_json(sys.argv[2])
    results = run_eval(lambda question: traced_rag(client, collection, question), cases)
    print(f"cases: {len(results)}   pass rate: {pass_rate(results)}   p95 ms: {percentile([r['ms'] for r in results], 95)}")
    for r in results:
        if not r["passed"]:
            print("failed:", r["id"], r.get("error", ""))
    if len(sys.argv) > 3:
        verdict = gate(load_json(sys.argv[3]), results)
        print("gate:", "ok" if verdict["ok"] else "BLOCKED: " + "; ".join(verdict["reasons"]))
    with open("last_results.json", "w", encoding="utf-8") as file:
        json.dump(results, file, indent=2)
    print("saved last_results.json (copy it to baseline.json when you accept the result)")


if __name__ == "__main__":
    main()
```

Write 10 to 20 cases in `evals/agent_cases.json`, like the example file. Include one question the docs cannot answer. Then:

```
python -m copilot.trace_cli ask "how do I delete a task"
python -m copilot.trace_cli eval evals/agent_cases.json
cp last_results.json baseline.json
```

Change something (the chunk size, a prompt line), run the eval with `baseline.json` as the third argument, and read the gate's verdict.

> A baseline is a decision: "this is the result I accept". Replace it only when you meant to.

### Checkpoint

Run the tests. Then look at one real trace and name the slowest span. Run the eval, save a baseline, make one change on purpose that should help, and write down what the gate said. If you cannot explain the verdict from the reasons, add a better reason text.
