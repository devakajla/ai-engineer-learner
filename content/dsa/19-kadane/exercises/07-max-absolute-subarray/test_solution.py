import random
from solution import max_abs_subarray


def brute(nums):
    best = 0
    for i in range(len(nums)):
        for j in range(i, len(nums)):
            best = max(best, abs(sum(nums[i:j + 1])))
    return best


def test_examples():
    assert max_abs_subarray([1, -3, 2, 3, -4]) == 5
    assert max_abs_subarray([2, -5, 1, -4, 3, -2]) == 8


def test_edges():
    assert max_abs_subarray([]) == 0
    assert max_abs_subarray([-5]) == 5
    assert max_abs_subarray([0, 0]) == 0


def test_random():
    rng = random.Random(7)
    for _ in range(300):
        nums = [rng.randint(-6, 6) for _ in range(rng.randint(0, 10))]
        assert max_abs_subarray(nums) == brute(nums), f"{nums}"
