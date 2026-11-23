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
