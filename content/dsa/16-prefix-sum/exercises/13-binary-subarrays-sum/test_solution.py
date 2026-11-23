import random
from solution import binary_subarrays_sum


def brute(nums, goal):
    return sum(1 for i in range(len(nums)) for j in range(i, len(nums)) if sum(nums[i:j + 1]) == goal)


def test_examples():
    assert binary_subarrays_sum([1, 0, 1, 0, 1], 2) == 4
    assert binary_subarrays_sum([0, 0, 0, 0, 0], 0) == 15


def test_edges():
    assert binary_subarrays_sum([], 0) == 0
    assert binary_subarrays_sum([1], 1) == 1
    assert binary_subarrays_sum([1, 1], 5) == 0


def test_random():
    rng = random.Random(12)
    for _ in range(300):
        nums = [rng.randint(0, 1) for _ in range(rng.randint(0, 12))]
        goal = rng.randint(0, 4)
        assert binary_subarrays_sum(nums, goal) == brute(nums, goal), f"{nums}, {goal}"
