import random
from solution import can_make_sum


def brute(nums, target):
    n = len(nums)
    return any(sum(nums[i] for i in range(n) if mask >> i & 1) == target for mask in range(1 << n))


def test_examples():
    assert can_make_sum([3, 34, 4, 12, 5, 2], 9) is True
    assert can_make_sum([3, 34], 10) is False


def test_edges():
    assert can_make_sum([], 0) is True
    assert can_make_sum([], 1) is False
    assert can_make_sum([0, 0], 0) is True


def test_random():
    rng = random.Random(13)
    for _ in range(300):
        nums = [rng.randint(0, 8) for _ in range(rng.randint(0, 7))]
        target = rng.randint(0, 20)
        assert can_make_sum(list(nums), target) is brute(nums, target), f"{nums}, {target}"
