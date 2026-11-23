import random
from itertools import combinations
from solution import subsets_with_dup


def brute(nums):
    return sorted({tuple(sorted(c)) for r in range(len(nums) + 1) for c in combinations(nums, r)})


def test_examples():
    assert sorted(subsets_with_dup([1, 2, 2])) == [[], [1], [1, 2], [1, 2, 2], [2], [2, 2]]
    assert sorted(subsets_with_dup([0])) == [[], [0]]


def test_random():
    rng = random.Random(14)
    for _ in range(100):
        v = [rng.randint(0, 3) for _ in range(rng.randint(0, 7))]
        got = subsets_with_dup(list(v))
        assert sorted(tuple(g) for g in got) == list(brute(v)), f"{v}"
        assert len(got) == len({tuple(g) for g in got}), f"{v}: duplicate subsets"
