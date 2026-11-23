import random
from solution import smallest_divisor


def brute(nums, t):
    d = 1
    while sum((n + d - 1) // d for n in nums) > t:
        d += 1
    return d


def test_examples():
    assert smallest_divisor([1, 2, 5, 9], 6) == 5
    assert smallest_divisor([44, 22, 33, 11, 1], 5) == 44


def test_edges():
    assert smallest_divisor([1], 1) == 1
    assert smallest_divisor([10], 1) == 10
    assert smallest_divisor([5, 5], 100) == 1


def test_random():
    rng = random.Random(16)
    for _ in range(300):
        nums = [rng.randint(1, 30) for _ in range(rng.randint(1, 6))]
        t = rng.randint(len(nums), len(nums) + 20)
        assert smallest_divisor(nums, t) == brute(nums, t), f"{nums}, {t}"
