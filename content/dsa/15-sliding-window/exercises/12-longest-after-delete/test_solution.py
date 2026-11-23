import random
from solution import longest_after_delete


def runs(nums):
    best = cur = 0
    for x in nums:
        cur = cur + 1 if x == 1 else 0
        best = max(best, cur)
    return best


def brute(nums):
    if not nums:
        return 0
    return max(runs(nums[:i] + nums[i + 1:]) for i in range(len(nums)))


def test_examples():
    assert longest_after_delete([1, 1, 0, 1]) == 3
    assert longest_after_delete([1, 1, 1]) == 2


def test_edges():
    assert longest_after_delete([0, 0]) == 0
    assert longest_after_delete([1]) == 0, "one item, you must delete it"
    assert longest_after_delete([0, 1, 1, 1, 0, 1, 1, 0, 1]) == 5


def test_random():
    rng = random.Random(12)
    for _ in range(300):
        nums = [rng.randint(0, 1) for _ in range(rng.randint(1, 12))]
        assert longest_after_delete(nums) == brute(nums), f"{nums}"
