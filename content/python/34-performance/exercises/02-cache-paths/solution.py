from functools import cache


@cache
def _ways(n):
    if n == 0:
        return 1
    if n < 0:
        return 0
    return _ways(n - 1) + _ways(n - 2) + _ways(n - 3)


def count_ways(n):
    if n < 0:
        raise ValueError("n must not be negative")
    return _ways(n)
