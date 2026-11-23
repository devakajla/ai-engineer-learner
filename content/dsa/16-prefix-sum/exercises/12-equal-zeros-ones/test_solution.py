import random
from solution import equal_zeros_ones


def brute(nums):
    best = 0
    for i in range(len(nums)):
        for j in range(i, len(nums)):
            part = nums[i:j + 1]
            if part.count(0) == part.count(1):
                best = max(best, len(part))
    return best


def test_examples():
    assert equal_zeros_ones([0, 1]) == 2
    assert equal_zeros_ones([0, 1, 0]) == 2


def test_edges():
    assert equal_zeros_ones([]) == 0
    assert equal_zeros_ones([1, 1, 1]) == 0
    assert equal_zeros_ones([0, 0, 1, 0, 0, 0, 1, 1]) == 6


def test_random():
    rng = random.Random(11)
    for _ in range(300):
        nums = [rng.randint(0, 1) for _ in range(rng.randint(0, 12))]
        assert equal_zeros_ones(nums) == brute(nums), f"{nums}"
