import random
from solution import contains_nearby_duplicate


def brute(nums, k):
    return any(nums[i] == nums[j] for i in range(len(nums)) for j in range(i + 1, min(len(nums), i + k + 1)))


def test_examples():
    assert contains_nearby_duplicate([1, 2, 3, 1], 3) is True
    assert contains_nearby_duplicate([1, 2, 3, 1, 2, 3], 2) is False


def test_edges():
    assert contains_nearby_duplicate([], 2) is False
    assert contains_nearby_duplicate([1, 1], 0) is False, "k = 0 means no pair is allowed"
    assert contains_nearby_duplicate([1, 0, 1, 1], 1) is True


def test_random():
    rng = random.Random(9)
    for _ in range(300):
        nums = [rng.randint(0, 5) for _ in range(rng.randint(0, 10))]
        k = rng.randint(0, 5)
        assert contains_nearby_duplicate(nums, k) is brute(nums, k), f"{nums}, {k}"
