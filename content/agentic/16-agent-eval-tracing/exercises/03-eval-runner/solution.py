# Given from earlier exercises. Do not change these.
def add_span(trace, name, kind, start, end, **attrs):
    span = {"name": name, "kind": kind, "ms": round((end - start) * 1000), **attrs}
    trace.append(span)
    return span


def trace_summary(trace):
    return {
        "spans": len(trace),
        "total_ms": sum(s["ms"] for s in trace),
        "llm_calls": sum(1 for s in trace if s["kind"] == "llm"),
        "tool_calls": sum(1 for s in trace if s["kind"] == "tool"),
        "tokens": sum(s.get("tokens", 0) for s in trace),
        "errors": sum(1 for s in trace if s.get("error")),
    }


def traced_call(trace, name, kind, clock, fn, *args, **kwargs):
    start = clock()
    try:
        result = fn(*args, **kwargs)
    except Exception as error:
        add_span(trace, name, kind, start, clock(), error=str(error))
        raise
    add_span(trace, name, kind, start, clock())
    return result


def tool_names(trace):
    return [span["name"] for span in trace if span["kind"] == "tool"]


def trajectory_match(actual, expected, mode="exact"):
    if mode == "exact":
        return actual == expected
    if mode == "in_order":
        remaining = iter(actual)
        return all(name in remaining for name in expected)
    if mode == "any_order":
        return all(name in actual for name in expected)
    raise ValueError(f"unknown mode: {mode}")


def step_efficiency(actual, expected):
    if not actual:
        return 1.0 if not expected else 0.0
    return round(min(1.0, len(expected) / len(actual)), 2)


# Your task:
def run_eval(agent, cases, mode="in_order"):
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


def pass_rate(results):
    if not results:
        return 0.0
    return round(sum(1 for r in results if r["passed"]) / len(results), 2)
