import random
from solution import min_join_cost


def brute(sticks):
    if len(sticks) <= 1:
        return 0
    best = float("inf")
    for i in range(len(sticks)):
        for j in range(i + 1, len(sticks)):
            rest = [s for k, s in enumerate(sticks) if k not in (i, j)]
            best = min(best, sticks[i] + sticks[j] + brute(rest + [sticks[i] + sticks[j]]))
    return best


def test_examples():
    assert min_join_cost([2, 4, 3]) == 14
    assert min_join_cost([7]) == 0


def test_random():
    rng = random.Random(6)
    for _ in range(200):
        sticks = [rng.randint(1, 9) for _ in range(rng.randint(0, 6))]
        assert min_join_cost(list(sticks)) == brute(sticks), f"{sticks}"
