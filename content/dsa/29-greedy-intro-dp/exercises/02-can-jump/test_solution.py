import random
from solution import can_jump


def brute(nums):
    ok = [False] * len(nums)
    ok[-1] = True
    for i in range(len(nums) - 2, -1, -1):
        ok[i] = any(ok[j] for j in range(i + 1, min(len(nums), i + nums[i] + 1)))
    return ok[0]


def test_examples():
    assert can_jump([2, 3, 1, 1, 4]) is True
    assert can_jump([3, 2, 1, 0, 4]) is False


def test_edges():
    assert can_jump([0]) is True
    assert can_jump([0, 1]) is False


def test_random():
    rng = random.Random(2)
    for _ in range(300):
        nums = [rng.randint(0, 3) for _ in range(rng.randint(1, 8))]
        assert can_jump(nums) is brute(nums), f"{nums}"
