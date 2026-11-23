import random
from solution import max_average


def brute(nums, k):
    return max(sum(nums[i:i + k]) for i in range(len(nums) - k + 1)) / k


def test_examples():
    assert abs(max_average([1, 12, -5, -6, 50, 3], 4) - 12.75) < 1e-9
    assert abs(max_average([5], 1) - 5.0) < 1e-9


def test_edges():
    assert abs(max_average([-1, -2, -3], 2) - (-1.5)) < 1e-9
    assert abs(max_average([0, 0, 0], 3)) < 1e-9


def test_random():
    rng = random.Random(8)
    for _ in range(200):
        n = rng.randint(1, 12)
        nums = [rng.randint(-9, 9) for _ in range(n)]
        k = rng.randint(1, n)
        assert abs(max_average(nums, k) - brute(nums, k)) < 1e-9, f"{nums}, {k}"
