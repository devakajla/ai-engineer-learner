import random
from solution import count_product_less


def brute(nums, k):
    total = 0
    for i in range(len(nums)):
        p = 1
        for j in range(i, len(nums)):
            p *= nums[j]
            if p < k:
                total += 1
    return total


def test_examples():
    assert count_product_less([10, 5, 2, 6], 100) == 8
    assert count_product_less([1, 2, 3], 0) == 0


def test_edges():
    assert count_product_less([], 10) == 0
    assert count_product_less([1, 1, 1], 1) == 0, "product must be strictly less"
    assert count_product_less([1, 1, 1], 2) == 6
    assert count_product_less([5], 5) == 0


def test_random():
    rng = random.Random(14)
    for _ in range(300):
        nums = [rng.randint(1, 6) for _ in range(rng.randint(0, 10))]
        k = rng.randint(0, 40)
        assert count_product_less(nums, k) == brute(nums, k), f"{nums}, {k}"
