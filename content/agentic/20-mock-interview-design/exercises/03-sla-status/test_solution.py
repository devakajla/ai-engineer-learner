from solution import sla_status


def test_healthy_service():
    out = sla_status([100, 200, 300, 400, 500], errors=1, total=200, p95_limit_ms=1000, max_error_rate=0.02)
    assert out == {"p95_ms": 500, "error_rate": 0.005, "ok": True, "problems": []}


def test_slow_tail_is_a_latency_problem_even_with_a_good_average():
    latencies = [100] * 19 + [5000]
    out = sla_status(latencies, errors=0, total=20, p95_limit_ms=1000, max_error_rate=0.05)
    assert out["p95_ms"] == 100, "one slow request in 20 is exactly the 95th percentile boundary"
    latencies = [100] * 18 + [5000, 5000]
    out = sla_status(latencies, errors=0, total=20, p95_limit_ms=1000, max_error_rate=0.05)
    assert out["p95_ms"] == 5000 and out["problems"] == ["latency"] and out["ok"] is False


def test_too_many_errors():
    out = sla_status([100] * 10, errors=5, total=100, p95_limit_ms=1000, max_error_rate=0.02)
    assert out["error_rate"] == 0.05
    assert out["problems"] == ["errors"] and out["ok"] is False


def test_both_problems_in_a_fixed_order():
    out = sla_status([3000] * 10, errors=50, total=100, p95_limit_ms=1000, max_error_rate=0.1)
    assert out["problems"] == ["latency", "errors"]


def test_exactly_on_the_limits_is_ok():
    out = sla_status([1000] * 5, errors=2, total=100, p95_limit_ms=1000, max_error_rate=0.02)
    assert out["ok"] is True


def test_no_traffic_is_ok():
    assert sla_status([], errors=0, total=0, p95_limit_ms=1000, max_error_rate=0.01) == {
        "p95_ms": 0, "error_rate": 0.0, "ok": True, "problems": []}
