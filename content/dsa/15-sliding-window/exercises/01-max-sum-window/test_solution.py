import random
from solution import max_sum_window


def brute(nums, k):
    return max(sum(nums[i:i + k]) for i in range(len(nums) - k + 1))


def test_examples():
    assert max_sum_window([2, 1, 5, 1, 3, 2], 3) == 9
    assert max_sum_window([4], 1) == 4


def test_edges():
    assert max_sum_window([-3, -1, -2], 2) == -3, "all negative numbers"
    assert max_sum_window([1, 2, 3], 3) == 6, "k equals the length"
    assert max_sum_window([5, -1, 5], 1) == 5


def test_random():
    rng = random.Random(1)
    for _ in range(200):
        n = rng.randint(1, 12)
        nums = [rng.randint(-9, 9) for _ in range(n)]
        k = rng.randint(1, n)
        assert max_sum_window(nums, k) == brute(nums, k), f"{nums}, {k}"
