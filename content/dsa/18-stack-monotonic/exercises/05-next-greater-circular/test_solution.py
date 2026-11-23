import random
from solution import next_greater_circular


def brute(nums):
    n = len(nums)
    out = []
    for i in range(n):
        out.append(next((nums[(i + k) % n] for k in range(1, n) if nums[(i + k) % n] > nums[i]), -1))
    return out


def test_examples():
    assert next_greater_circular([1, 2, 1]) == [2, -1, 2]
    assert next_greater_circular([1, 2, 3, 4, 3]) == [2, 3, 4, -1, 4]


def test_edges():
    assert next_greater_circular([]) == []
    assert next_greater_circular([7]) == [-1]
    assert next_greater_circular([3, 3]) == [-1, -1]
    assert next_greater_circular([5, 1]) == [-1, 5]


def test_random():
    rng = random.Random(5)
    for _ in range(300):
        nums = [rng.randint(0, 5) for _ in range(rng.randint(0, 9))]
        assert next_greater_circular(nums) == brute(nums), f"{nums}"
