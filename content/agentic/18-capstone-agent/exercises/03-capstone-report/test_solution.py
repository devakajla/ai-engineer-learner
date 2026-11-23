from solution import capstone_report, format_report, percentile


def r(id, passed, steps=1, tokens=100, ms=1000):
    return {"id": id, "passed": passed, "steps": steps, "tokens": tokens, "ms": ms}


def test_percentile_uses_the_nearest_rank_method():
    values = list(range(1, 101))
    assert percentile(values, 95) == 95
    assert percentile(values, 50) == 50
    assert percentile([10, 20, 30], 95) == 30
    assert percentile([7], 95) == 7
    assert percentile([], 95) == 0


def test_percentile_does_not_need_sorted_input():
    assert percentile([30, 10, 20], 50) == 20


def test_report_numbers():
    results = [r("a", True, 2, 100, 800), r("b", False, 4, 300, 3000), r("c", True, 3, 200, 1200), r("d", True, 3, 400, 900)]
    assert capstone_report(results) == {
        "cases": 4, "pass_rate": 0.75, "avg_steps": 3.0, "total_tokens": 1000, "p95_ms": 3000, "failed": ["b"]}


def test_empty_report():
    assert capstone_report([]) == {"cases": 0, "pass_rate": 0.0, "avg_steps": 0.0, "total_tokens": 0, "p95_ms": 0, "failed": []}


def test_format_report_with_failures():
    report = {"cases": 4, "pass_rate": 0.75, "avg_steps": 3.0, "total_tokens": 1000, "p95_ms": 3000, "failed": ["b", "e"]}
    assert format_report(report) == (
        "Cases: 4\nPass rate: 75%\nAverage steps: 3.0\nTotal tokens: 1000\np95 latency: 3000 ms\nFailed: b, e")


def test_format_report_without_failures():
    report = capstone_report([r("a", True)])
    assert format_report(report).endswith("Failed: none")
    assert "Pass rate: 100%" in format_report(report)
