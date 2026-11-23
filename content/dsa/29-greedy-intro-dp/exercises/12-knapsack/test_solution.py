import random
from solution import knapsack


def brute(weights, values, capacity):
    best = 0
    n = len(weights)
    for mask in range(1 << n):
        wt = sum(weights[i] for i in range(n) if mask >> i & 1)
        if wt <= capacity:
            best = max(best, sum(values[i] for i in range(n) if mask >> i & 1))
    return best


def test_examples():
    assert knapsack([1, 3, 4], [15, 20, 30], 4) == 35
    assert knapsack([5], [10], 4) == 0


def test_edges():
    assert knapsack([], [], 10) == 0
    assert knapsack([2], [7], 2) == 7


def test_random():
    rng = random.Random(12)
    for _ in range(300):
        n = rng.randint(0, 7)
        weights = [rng.randint(1, 6) for _ in range(n)]
        values = [rng.randint(0, 9) for _ in range(n)]
        cap = rng.randint(0, 12)
        assert knapsack(list(weights), list(values), cap) == brute(weights, values, cap), f"{weights}, {values}, {cap}"
