import random
from solution import stock_spans


def brute(prices):
    out = []
    for i, p in enumerate(prices):
        span = 1
        while i - span >= 0 and prices[i - span] <= p:
            span += 1
        out.append(span)
    return out


def test_examples():
    assert stock_spans([100, 80, 60, 70, 60, 75, 85]) == [1, 1, 1, 2, 1, 4, 6]
    assert stock_spans([10, 10, 10]) == [1, 2, 3]


def test_edges():
    assert stock_spans([]) == []
    assert stock_spans([5]) == [1]
    assert stock_spans([9, 8, 7]) == [1, 1, 1]


def test_random():
    rng = random.Random(14)
    for _ in range(300):
        prices = [rng.randint(1, 6) for _ in range(rng.randint(0, 10))]
        assert stock_spans(prices) == brute(prices), f"{prices}"
