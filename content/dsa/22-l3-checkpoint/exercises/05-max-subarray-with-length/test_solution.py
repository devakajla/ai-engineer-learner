import random
from solution import best_sums


def brute(nums, k):
    n = len(nums)
    win = max(sum(nums[i:i + k]) for i in range(n - k + 1))
    anyv = max(sum(nums[i:j + 1]) for i in range(n) for j in range(i, n))
    return (win, anyv)


def test_examples():
    assert best_sums([1, -2, 3, 4, -1], 2) == (7, 7)
    assert best_sums([-3, -1, -2], 2) == (-3, -1)


def test_edges():
    assert best_sums([5], 1) == (5, 5)
    assert best_sums([-5], 1) == (-5, -5)


def test_random():
    rng = random.Random(5)
    for _ in range(300):
        nums = [rng.randint(-8, 8) for _ in range(rng.randint(1, 9))]
        k = rng.randint(1, len(nums))
        assert best_sums(nums, k) == brute(nums, k), f"{nums}, {k}"
