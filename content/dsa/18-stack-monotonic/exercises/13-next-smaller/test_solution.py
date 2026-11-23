import random
from solution import next_smaller


def brute(nums):
    return [next((y for y in nums[i + 1:] if y < x), -1) for i, x in enumerate(nums)]


def test_examples():
    assert next_smaller([4, 8, 5, 2, 25]) == [2, 5, 2, -1, -1]
    assert next_smaller([1, 2, 3]) == [-1, -1, -1]


def test_edges():
    assert next_smaller([]) == []
    assert next_smaller([3, 3]) == [-1, -1]


def test_random():
    rng = random.Random(13)
    for _ in range(300):
        nums = [rng.randint(0, 6) for _ in range(rng.randint(0, 10))]
        assert next_smaller(nums) == brute(nums), f"{nums}"
