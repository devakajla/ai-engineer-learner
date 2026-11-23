import random
from solution import max_profit


def brute(prices):
    n = len(prices)
    hold, free = float("-inf"), 0
    for p in prices:
        hold, free = max(hold, free - p), max(free, hold + p)
    return free


def test_examples():
    assert max_profit([7, 1, 5, 3, 6, 4]) == 7
    assert max_profit([5, 4, 3]) == 0


def test_edges():
    assert max_profit([]) == 0
    assert max_profit([3]) == 0


def test_random():
    rng = random.Random(4)
    for _ in range(300):
        prices = [rng.randint(0, 9) for _ in range(rng.randint(0, 9))]
        assert max_profit(prices) == brute(prices), f"{prices}"
