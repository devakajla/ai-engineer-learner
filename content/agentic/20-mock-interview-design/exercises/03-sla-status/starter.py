import math


def percentile(values, p):
    if not values:
        return 0
    ordered = sorted(values)
    rank = math.ceil(p / 100 * len(ordered))
    return ordered[max(rank, 1) - 1]


def sla_status(latencies_ms, errors, total, p95_limit_ms, max_error_rate):
    ...
