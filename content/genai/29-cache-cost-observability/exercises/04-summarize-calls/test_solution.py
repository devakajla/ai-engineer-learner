from solution import summarize_calls

CALLS = [
    {"model": "m", "input": 1000, "output": 500, "ms": 800, "ok": True},
    {"model": "m", "input": 2000, "output": 0, "ms": 2000, "ok": False},
]


def test_example():
    out = summarize_calls(CALLS, {"m": (1.0, 2.0)})
    assert out == {
        "n": 2, "errors": 1, "error_rate": 0.5, "total_cost": 0.004,
        "avg_ms": 1400.0, "p95_ms": 2000, "unpriced": 0,
    }


def test_unpriced_models():
    calls = CALLS + [{"model": "new", "input": 10, "output": 10, "ms": 100, "ok": True}]
    out = summarize_calls(calls, {"m": (1.0, 2.0)})
    assert out["unpriced"] == 1 and out["total_cost"] == 0.004 and out["n"] == 3


def test_p95_of_twenty():
    calls = [{"model": "m", "input": 0, "output": 0, "ms": i * 10, "ok": True} for i in range(1, 21)]
    out = summarize_calls(calls, {"m": (1.0, 1.0)})
    assert out["p95_ms"] == 190, "index ceil(0.95 * 20) - 1 = 18 of the sorted times"
    assert out["avg_ms"] == 105.0


def test_p95_unsorted_input():
    calls = [{"model": "m", "input": 0, "output": 0, "ms": ms, "ok": True} for ms in (500, 100, 300)]
    assert summarize_calls(calls, {"m": (1.0, 1.0)})["p95_ms"] == 500


def test_empty():
    assert summarize_calls([], {}) == {
        "n": 0, "errors": 0, "error_rate": 0.0, "total_cost": 0.0, "avg_ms": 0.0, "p95_ms": 0, "unpriced": 0,
    }


def test_error_rate_rounding():
    calls = [{"model": "m", "input": 0, "output": 0, "ms": 1, "ok": i != 0} for i in range(3)]
    assert summarize_calls(calls, {"m": (1.0, 1.0)})["error_rate"] == 0.3333
