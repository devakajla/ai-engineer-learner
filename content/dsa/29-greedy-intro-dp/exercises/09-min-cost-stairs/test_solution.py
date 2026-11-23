import random
from solution import min_cost


def brute(cost):
    n = len(cost)
    memo = {}

    def go(i):
        if i >= n:
            return 0
        if i not in memo:
            memo[i] = cost[i] + min(go(i + 1), go(i + 2))
        return memo[i]

    return min(go(0), go(1))


def test_examples():
    assert min_cost([10, 15, 20]) == 15
    assert min_cost([1, 100, 1, 1, 1, 100, 1, 1, 100, 1]) == 6


def test_random():
    rng = random.Random(9)
    for _ in range(300):
        cost = [rng.randint(0, 9) for _ in range(rng.randint(2, 9))]
        assert min_cost(list(cost)) == brute(cost), f"{cost}"
