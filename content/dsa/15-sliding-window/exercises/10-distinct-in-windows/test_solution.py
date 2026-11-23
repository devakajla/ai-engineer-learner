import random
from solution import distinct_in_windows


def brute(nums, k):
    return [len(set(nums[i:i + k])) for i in range(len(nums) - k + 1)]


def test_examples():
    assert distinct_in_windows([1, 2, 1, 3, 4, 2, 3], 4) == [3, 4, 4, 3]
    assert distinct_in_windows([5, 5, 5], 2) == [1, 1]


def test_edges():
    assert distinct_in_windows([7], 1) == [1]
    assert distinct_in_windows([1, 2, 3], 3) == [3]
    assert distinct_in_windows([1, 2, 3], 1) == [1, 1, 1]


def test_random():
    rng = random.Random(10)
    for _ in range(300):
        n = rng.randint(1, 12)
        nums = [rng.randint(0, 4) for _ in range(n)]
        k = rng.randint(1, n)
        assert distinct_in_windows(nums, k) == brute(nums, k), f"{nums}, {k}"
