import random
from solution import next_greater


def brute(nums):
    out = []
    for i, x in enumerate(nums):
        out.append(next((y for y in nums[i + 1:] if y > x), -1))
    return out


def test_examples():
    assert next_greater([4, 1, 2]) == [-1, 2, -1]
    assert next_greater([1, 3, 2, 4]) == [3, 4, 4, -1]


def test_edges():
    assert next_greater([]) == []
    assert next_greater([5]) == [-1]
    assert next_greater([2, 2, 2]) == [-1, -1, -1], "equal is not greater"
    assert next_greater([5, 4, 3]) == [-1, -1, -1]


def test_random():
    rng = random.Random(3)
    for _ in range(300):
        nums = [rng.randint(0, 6) for _ in range(rng.randint(0, 10))]
        assert next_greater(nums) == brute(nums), f"{nums}"
