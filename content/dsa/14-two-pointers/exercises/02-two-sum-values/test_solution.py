import random
from solution import two_sum_values


def brute(nums, target):
    best = None
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                pair = sorted([nums[i], nums[j]])
                if best is None or pair[0] < best[0]:
                    best = pair
    return best or []


def test_examples():
    assert two_sum_values([7, 2, 11, 4], 9) == [2, 7]
    assert two_sum_values([3, 3], 6) == [3, 3]


def test_edges():
    assert two_sum_values([], 0) == []
    assert two_sum_values([4], 8) == [], "needs two different positions"
    assert two_sum_values([1, 2], 7) == []
    assert two_sum_values([-3, 9, 3, 0], 0) == [-3, 3]


def test_does_not_change_input():
    nums = [5, 1, 4]
    two_sum_values(nums, 9)
    assert nums == [5, 1, 4], "work on a sorted copy"


def test_random():
    rng = random.Random(2)
    for _ in range(300):
        nums = [rng.randint(-8, 8) for _ in range(rng.randint(0, 8))]
        t = rng.randint(-12, 12)
        assert two_sum_values(nums, t) == brute(nums, t), f"{nums}, {t}"
