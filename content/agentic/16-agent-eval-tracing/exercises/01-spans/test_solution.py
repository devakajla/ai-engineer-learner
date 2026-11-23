import pytest

from solution import add_span, trace_summary, traced_call


def make_clock(*times):
    items = iter(times)
    return lambda: next(items)


def test_add_span_records_name_kind_duration_and_extras():
    trace = []
    span = add_span(trace, "llm", "llm", 1.0, 1.25, tokens=120)
    assert span == {"name": "llm", "kind": "llm", "ms": 250, "tokens": 120}
    assert trace == [span]


def test_summary_counts_everything():
    trace = []
    add_span(trace, "llm", "llm", 0.0, 0.5, tokens=100)
    add_span(trace, "search", "tool", 0.5, 0.6)
    add_span(trace, "llm", "llm", 0.6, 1.0, tokens=60)
    add_span(trace, "calc", "tool", 1.0, 1.1, error="bad input")
    assert trace_summary(trace) == {
        "spans": 4, "total_ms": 1100, "llm_calls": 2, "tool_calls": 2, "tokens": 160, "errors": 1}


def test_empty_trace_summary():
    assert trace_summary([]) == {"spans": 0, "total_ms": 0, "llm_calls": 0, "tool_calls": 0, "tokens": 0, "errors": 0}


def test_traced_call_returns_the_result_and_records_a_span():
    trace = []
    result = traced_call(trace, "add", "tool", make_clock(10.0, 10.2), lambda a, b: a + b, 2, b=3)
    assert result == 5
    assert trace == [{"name": "add", "kind": "tool", "ms": 200}]


def test_traced_call_records_the_error_and_re_raises():
    trace = []

    def boom():
        raise ValueError("no good")

    with pytest.raises(ValueError, match="no good"):
        traced_call(trace, "boom", "tool", make_clock(0.0, 0.05), boom)
    assert trace == [{"name": "boom", "kind": "tool", "ms": 50, "error": "no good"}]
