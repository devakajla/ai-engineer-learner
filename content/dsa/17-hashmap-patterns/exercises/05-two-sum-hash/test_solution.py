import random
from solution import two_sum


def exists(nums, target):
    return any(nums[i] + nums[j] == target for i in range(len(nums)) for j in range(i + 1, len(nums)))


def check(nums, target):
    res = two_sum(nums, target)
    if exists(nums, target):
        assert len(res) == 2, f"{nums}, {target}: pair exists, got {res}"
        i, j = res
        assert 0 <= i < j < len(nums) and nums[i] + nums[j] == target, f"{nums}, {target}: bad answer {res}"
    else:
        assert res == [], f"{nums}, {target}: expected [], got {res}"


def test_examples():
    assert two_sum([2, 7, 11, 15], 9) == [0, 1]
    assert two_sum([3, 3], 6) == [0, 1]


def test_edges():
    check([], 1)
    check([5], 5)
    check([3, 2, 4], 6)
    check([4], 8)


def test_random():
    rng = random.Random(5)
    for _ in range(300):
        nums = [rng.randint(-5, 9) for _ in range(rng.randint(0, 8))]
        check(nums, rng.randint(-6, 12))
