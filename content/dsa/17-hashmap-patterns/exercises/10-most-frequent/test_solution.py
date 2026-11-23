import random
from solution import most_frequent


def brute(nums):
    if not nums:
        return None
    top = max(nums.count(x) for x in nums)
    return min(x for x in nums if nums.count(x) == top)


def test_examples():
    assert most_frequent([1, 3, 2, 3, 2]) == 2
    assert most_frequent([5]) == 5


def test_edges():
    assert most_frequent([]) is None
    assert most_frequent([-1, -1, 2, 2]) == -1
    assert most_frequent([4, 4, 4, 1, 1]) == 4


def test_random():
    rng = random.Random(10)
    for _ in range(300):
        nums = [rng.randint(-3, 3) for _ in range(rng.randint(0, 10))]
        assert most_frequent(nums) == brute(nums), f"{nums}"
