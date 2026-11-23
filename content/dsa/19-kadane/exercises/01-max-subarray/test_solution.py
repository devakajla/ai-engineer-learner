import random
from solution import max_subarray


def brute(nums):
    return max(sum(nums[i:j + 1]) for i in range(len(nums)) for j in range(i, len(nums)))


def test_examples():
    assert max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6
    assert max_subarray([-3, -1, -2]) == -1


def test_edges():
    assert max_subarray([5]) == 5
    assert max_subarray([-7]) == -7, "must be non-empty"
    assert max_subarray([1, 2, 3]) == 6
    assert max_subarray([0, 0]) == 0


def test_random():
    rng = random.Random(1)
    for _ in range(300):
        nums = [rng.randint(-8, 8) for _ in range(rng.randint(1, 12))]
        assert max_subarray(nums) == brute(nums), f"{nums}"
