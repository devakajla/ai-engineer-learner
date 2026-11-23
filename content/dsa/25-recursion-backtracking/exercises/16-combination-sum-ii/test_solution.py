import random
from itertools import combinations
from solution import combination_sum2


def brute(c, t):
    return sorted({tuple(sorted(x)) for r in range(1, len(c) + 1) for x in combinations(c, r) if sum(x) == t})


def test_examples():
    assert sorted(combination_sum2([10, 1, 2, 7, 6, 1, 5], 8)) == [[1, 1, 6], [1, 2, 5], [1, 7], [2, 6]]
    assert sorted(combination_sum2([2, 5, 2, 1, 2], 5)) == [[1, 2, 2], [5]]


def test_random():
    rng = random.Random(16)
    for _ in range(100):
        c = [rng.randint(1, 6) for _ in range(rng.randint(1, 8))]
        t = rng.randint(1, 12)
        got = combination_sum2(list(c), t)
        assert sorted(tuple(g) for g in got) == list(brute(c, t)), f"{c}, {t}"
        assert len(got) == len({tuple(g) for g in got}), f"{c}, {t}: duplicate combinations"
