import random
from solution import min_subarray


def brute(nums):
    return min(sum(nums[i:j + 1]) for i in range(len(nums)) for j in range(i, len(nums)))


def test_examples():
    assert min_subarray([3, -4, 2, -3, -1, 7, -5]) == -6
    assert min_subarray([1, 2, 3]) == 1


def test_edges():
    assert min_subarray([4]) == 4
    assert min_subarray([-1, -2]) == -3


def test_random():
    rng = random.Random(6)
    for _ in range(300):
        nums = [rng.randint(-8, 8) for _ in range(rng.randint(1, 12))]
        assert min_subarray(nums) == brute(nums), f"{nums}"
