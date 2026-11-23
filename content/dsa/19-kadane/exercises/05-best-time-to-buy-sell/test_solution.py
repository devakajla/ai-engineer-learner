import random
from solution import max_profit


def brute(prices):
    best = 0
    for i in range(len(prices)):
        for j in range(i + 1, len(prices)):
            best = max(best, prices[j] - prices[i])
    return best


def test_examples():
    assert max_profit([7, 1, 5, 3, 6, 4]) == 5
    assert max_profit([7, 6, 4, 3, 1]) == 0


def test_edges():
    assert max_profit([]) == 0
    assert max_profit([5]) == 0
    assert max_profit([2, 4, 1]) == 2, "you cannot sell before you buy"
    assert max_profit([3, 3]) == 0


def test_random():
    rng = random.Random(5)
    for _ in range(300):
        prices = [rng.randint(1, 9) for _ in range(rng.randint(0, 10))]
        assert max_profit(prices) == brute(prices), f"{prices}"
