import random
from solution import rob


def brute(nums):
    best = 0
    n = len(nums)
    for mask in range(1 << n):
        if mask & (mask >> 1):
            continue
        best = max(best, sum(nums[i] for i in range(n) if mask >> i & 1))
    return best


def test_examples():
    assert rob([1, 2, 3, 1]) == 4
    assert rob([2, 7, 9, 3, 1]) == 12


def test_edges():
    assert rob([]) == 0
    assert rob([5]) == 5


def test_random():
    rng = random.Random(8)
    for _ in range(300):
        nums = [rng.randint(0, 9) for _ in range(rng.randint(0, 9))]
        assert rob(nums) == brute(nums), f"{nums}"
