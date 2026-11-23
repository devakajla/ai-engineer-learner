import random
from solution import count_pairs_sum


def brute(nums, target):
    return sum(1 for i in range(len(nums)) for j in range(i + 1, len(nums)) if nums[i] + nums[j] == target)


def test_examples():
    assert count_pairs_sum([1, 5, 7, -1, 5], 6) == 3
    assert count_pairs_sum([1, 1, 1, 1], 2) == 6


def test_edges():
    assert count_pairs_sum([], 0) == 0
    assert count_pairs_sum([3], 6) == 0, "an item cannot pair with itself"
    assert count_pairs_sum([0, 0, 0], 0) == 3


def test_random():
    rng = random.Random(16)
    for _ in range(300):
        nums = [rng.randint(-4, 6) for _ in range(rng.randint(0, 10))]
        t = rng.randint(-4, 8)
        assert count_pairs_sum(nums, t) == brute(nums, t), f"{nums}, {t}"
