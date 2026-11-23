import random
from solution import longest_sum_k


def brute(nums, k):
    best = 0
    for i in range(len(nums)):
        for j in range(i, len(nums)):
            if sum(nums[i:j + 1]) == k:
                best = max(best, j - i + 1)
    return best


def test_examples():
    assert longest_sum_k([1, -1, 5, -2, 3], 3) == 4
    assert longest_sum_k([-2, -1, 2, 1], 1) == 2


def test_edges():
    assert longest_sum_k([], 0) == 0
    assert longest_sum_k([0, 0, 0], 0) == 3, "prefix 0 must start at index -1"
    assert longest_sum_k([1, 2], 10) == 0


def test_random():
    rng = random.Random(9)
    for _ in range(300):
        nums = [rng.randint(-3, 3) for _ in range(rng.randint(0, 10))]
        k = rng.randint(-4, 4)
        assert longest_sum_k(nums, k) == brute(nums, k), f"{nums}, {k}"
