import random
from solution import max_len_positive_product


def brute(nums):
    best = 0
    for i in range(len(nums)):
        p = 1
        for j in range(i, len(nums)):
            p *= nums[j]
            if p > 0:
                best = max(best, j - i + 1)
    return best


def test_examples():
    assert max_len_positive_product([1, -2, -3, 4]) == 4
    assert max_len_positive_product([0, 1, -2, -3, -4]) == 3


def test_edges():
    assert max_len_positive_product([]) == 0
    assert max_len_positive_product([-1, -2, -3, 0, 1]) == 2
    assert max_len_positive_product([-1]) == 0
    assert max_len_positive_product([0, 0]) == 0


def test_random():
    rng = random.Random(9)
    for _ in range(400):
        nums = [rng.randint(-2, 2) for _ in range(rng.randint(0, 10))]
        assert max_len_positive_product(nums) == brute(nums), f"{nums}"
