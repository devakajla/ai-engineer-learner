import random
from solution import longest_ones


def brute(nums, k):
    best = 0
    for i in range(len(nums)):
        for j in range(i, len(nums)):
            if nums[i:j + 1].count(0) <= k:
                best = max(best, j - i + 1)
    return best


def test_examples():
    assert longest_ones([1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], 2) == 6
    assert longest_ones([0, 0, 0], 0) == 0


def test_edges():
    assert longest_ones([], 2) == 0
    assert longest_ones([0, 0, 0], 5) == 3
    assert longest_ones([1, 1, 1], 0) == 3


def test_random():
    rng = random.Random(11)
    for _ in range(300):
        nums = [rng.randint(0, 1) for _ in range(rng.randint(0, 14))]
        k = rng.randint(0, 4)
        assert longest_ones(nums, k) == brute(nums, k), f"{nums}, {k}"
