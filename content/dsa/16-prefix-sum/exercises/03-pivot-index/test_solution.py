import random
from solution import pivot_index


def brute(nums):
    for i in range(len(nums)):
        if sum(nums[:i]) == sum(nums[i + 1:]):
            return i
    return -1


def test_examples():
    assert pivot_index([1, 7, 3, 6, 5, 6]) == 3
    assert pivot_index([1, 2, 3]) == -1


def test_edges():
    assert pivot_index([2, 1, -1]) == 0, "left side is empty (sum 0)"
    assert pivot_index([]) == -1
    assert pivot_index([5]) == 0
    assert pivot_index([0, 0, 0]) == 0, "leftmost"


def test_random():
    rng = random.Random(2)
    for _ in range(300):
        nums = [rng.randint(-3, 3) for _ in range(rng.randint(0, 9))]
        assert pivot_index(nums) == brute(nums), f"{nums}"
