import random
from solution import two_sum_sorted


def exists(nums, target):
    return any(nums[i] + nums[j] == target for i in range(len(nums)) for j in range(i + 1, len(nums)))


def check(nums, target):
    res = two_sum_sorted(nums, target)
    if exists(nums, target):
        assert len(res) == 2, f"{nums}, {target}: a pair exists but got {res}"
        i, j = res
        assert 0 <= i < j < len(nums), f"need 0 <= i < j, got {res}"
        assert nums[i] + nums[j] == target, f"{nums}, {target}: {res} does not add up"
    else:
        assert res == [], f"{nums}, {target}: no pair, expected [] got {res}"


def test_examples():
    assert two_sum_sorted([1, 2, 4, 7, 11], 9) == [1, 3]
    assert two_sum_sorted([1, 2, 3], 10) == []


def test_edges():
    check([], 1)
    check([5], 5)
    check([3, 3], 6)
    check([-4, -1, 0, 3, 10], 9)
    check([-5, -3, 0], -8)
    check([2, 2, 2], 5)


def test_random():
    rng = random.Random(1)
    for _ in range(300):
        nums = sorted(rng.randint(-10, 10) for _ in range(rng.randint(0, 8)))
        check(nums, rng.randint(-15, 15))
