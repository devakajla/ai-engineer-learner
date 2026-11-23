import math


def percentile(values, p):
    if not values:
        return 0
    ordered = sorted(values)
    rank = math.ceil(p / 100 * len(ordered))
    return ordered[max(rank, 1) - 1]


def sla_status(latencies_ms, errors, total, p95_limit_ms, max_error_rate):
    p95 = percentile(latencies_ms, 95)
    error_rate = round(errors / total, 4) if total else 0.0
    problems = []
    if p95 > p95_limit_ms:
        problems.append("latency")
    if error_rate > max_error_rate:
        problems.append("errors")
    return {"p95_ms": p95, "error_rate": error_rate, "ok": not problems, "problems": problems}
