import random
from solution import max_profit_many


def brute(prices):
    # dp over days: (cash, holding)
    cash, hold = 0, float("-inf")
    for p in prices:
        cash, hold = max(cash, hold + p), max(hold, cash - p)
    return cash


def test_examples():
    assert max_profit_many([7, 1, 5, 3, 6, 4]) == 7
    assert max_profit_many([1, 2, 3, 4, 5]) == 4


def test_edges():
    assert max_profit_many([]) == 0
    assert max_profit_many([5]) == 0
    assert max_profit_many([5, 4, 3]) == 0


def test_random():
    rng = random.Random(15)
    for _ in range(300):
        prices = [rng.randint(1, 9) for _ in range(rng.randint(0, 10))]
        assert max_profit_many(prices) == brute(prices), f"{prices}"
