import random
from itertools import combinations
from solution import subsets


def brute(nums):
    return sorted(list(c) for r in range(len(nums) + 1) for c in combinations(nums, r))


def test_examples():
    assert sorted(subsets([1, 2])) == [[], [1], [1, 2], [2]]
    assert subsets([]) == [[]]


def test_random():
    rng = random.Random(6)
    for _ in range(100):
        v = rng.sample(range(-9, 10), rng.randint(0, 7))
        assert sorted(subsets(list(v))) == brute(v), f"{v}"
