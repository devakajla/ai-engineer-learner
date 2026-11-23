import random
from solution import max_sum_at_least_k


def brute(nums, k):
    return max(sum(nums[i:j + 1]) for i in range(len(nums)) for j in range(i + k - 1, len(nums)))


def test_examples():
    assert max_sum_at_least_k([-1, -2, 3, 4, -5], 2) == 7
    assert max_sum_at_least_k([-5, -3], 2) == -8


def test_edges():
    assert max_sum_at_least_k([4], 1) == 4
    assert max_sum_at_least_k([1, 2, 3], 3) == 6
    assert max_sum_at_least_k([5, -10, 5], 1) == 5


def test_random():
    rng = random.Random(13)
    for _ in range(300):
        n = rng.randint(1, 10)
        nums = [rng.randint(-6, 6) for _ in range(n)]
        k = rng.randint(1, n)
        assert max_sum_at_least_k(nums, k) == brute(nums, k), f"{nums}, {k}"
