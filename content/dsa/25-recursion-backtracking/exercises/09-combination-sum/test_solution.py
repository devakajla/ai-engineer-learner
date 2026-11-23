import random
from itertools import combinations_with_replacement
from solution import combination_sum


def brute(c, t):
    out = []
    for r in range(1, t + 1):
        for combo in combinations_with_replacement(c, r):
            if sum(combo) == t:
                out.append(list(combo))
    return sorted(out)


def test_examples():
    assert sorted(combination_sum([2, 3, 6, 7], 7)) == [[2, 2, 3], [7]]
    assert combination_sum([2], 1) == []


def test_edges():
    assert combination_sum([1], 3) == [[1, 1, 1]]


def test_random():
    rng = random.Random(9)
    for _ in range(100):
        c = sorted(rng.sample(range(1, 8), rng.randint(1, 4)))
        t = rng.randint(1, 10)
        assert sorted(combination_sum(list(c), t)) == brute(c, t), f"{c}, {t}"
