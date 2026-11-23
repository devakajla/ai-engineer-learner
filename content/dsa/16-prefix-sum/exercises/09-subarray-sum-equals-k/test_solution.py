import random
from solution import subarray_sum_k


def brute(nums, k):
    return sum(1 for i in range(len(nums)) for j in range(i, len(nums)) if sum(nums[i:j + 1]) == k)


def test_examples():
    assert subarray_sum_k([1, 1, 1], 2) == 2
    assert subarray_sum_k([1, 2, 3], 3) == 2


def test_edges():
    assert subarray_sum_k([], 0) == 0
    assert subarray_sum_k([0, 0, 0], 0) == 6
    assert subarray_sum_k([1, -1, 0], 0) == 3, "negatives and zeros"


def test_random():
    rng = random.Random(8)
    for _ in range(300):
        nums = [rng.randint(-3, 3) for _ in range(rng.randint(0, 10))]
        k = rng.randint(-4, 4)
        assert subarray_sum_k(nums, k) == brute(nums, k), f"{nums}, {k}"
