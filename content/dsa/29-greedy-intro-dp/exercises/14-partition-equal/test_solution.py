import random
from solution import can_partition


def brute(nums):
    total = sum(nums)
    n = len(nums)
    return any(2 * sum(nums[i] for i in range(n) if mask >> i & 1) == total for mask in range(1 << n))


def test_examples():
    assert can_partition([1, 5, 11, 5]) is True
    assert can_partition([1, 2, 3, 5]) is False


def test_edges():
    assert can_partition([]) is True
    assert can_partition([2]) is False


def test_random():
    rng = random.Random(14)
    for _ in range(300):
        nums = [rng.randint(1, 8) for _ in range(rng.randint(0, 8))]
        assert can_partition(list(nums)) is brute(nums), f"{nums}"
