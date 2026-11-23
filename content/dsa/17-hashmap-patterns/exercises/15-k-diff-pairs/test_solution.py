import random
from solution import k_diff_pairs


def brute(nums, k):
    found = set()
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if abs(nums[i] - nums[j]) == k:
                found.add((min(nums[i], nums[j]), max(nums[i], nums[j])))
    return len(found)


def test_examples():
    assert k_diff_pairs([3, 1, 4, 1, 5], 2) == 2
    assert k_diff_pairs([1, 3, 1, 5, 4], 0) == 1


def test_edges():
    assert k_diff_pairs([], 1) == 0
    assert k_diff_pairs([1, 2, 3, 4, 5], 1) == 4
    assert k_diff_pairs([1], 0) == 0


def test_random():
    rng = random.Random(15)
    for _ in range(300):
        nums = [rng.randint(-4, 4) for _ in range(rng.randint(0, 9))]
        k = rng.randint(0, 5)
        assert k_diff_pairs(nums, k) == brute(nums, k), f"{nums}, {k}"
