import random
from solution import count_divisible


def brute(nums, k):
    return sum(1 for i in range(len(nums)) for j in range(i, len(nums)) if sum(nums[i:j + 1]) % k == 0)


def test_examples():
    assert count_divisible([4, 5, 0, -2, -3, 1], 5) == 7
    assert count_divisible([5], 9) == 0


def test_edges():
    assert count_divisible([], 3) == 0
    assert count_divisible([3], 3) == 1
    assert count_divisible([0, 0, 0], 7) == 6


def test_random():
    rng = random.Random(3)
    for _ in range(300):
        nums = [rng.randint(-6, 6) for _ in range(rng.randint(0, 10))]
        k = rng.randint(1, 6)
        assert count_divisible(nums, k) == brute(nums, k), f"{nums}, {k}"
