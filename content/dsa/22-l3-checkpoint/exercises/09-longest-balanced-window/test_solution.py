import random
from solution import longest_sum_at_most


def brute(nums, k):
    best = 0
    for i in range(len(nums)):
        for j in range(i, len(nums)):
            if sum(nums[i:j + 1]) <= k:
                best = max(best, j - i + 1)
    return best


def test_examples():
    assert longest_sum_at_most([1, 2, 1, 0, 1, 1, 0], 4) == 5
    assert longest_sum_at_most([5, 6], 4) == 0


def test_edges():
    assert longest_sum_at_most([], 3) == 0
    assert longest_sum_at_most([0, 0], 0) == 2
    assert longest_sum_at_most([2], 2) == 1


def test_random():
    rng = random.Random(9)
    for _ in range(300):
        nums = [rng.randint(0, 5) for _ in range(rng.randint(0, 10))]
        k = rng.randint(0, 12)
        assert longest_sum_at_most(nums, k) == brute(nums, k), f"{nums}, {k}"
