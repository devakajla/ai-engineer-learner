import random
from solution import num_ways_split


def test_examples():
    assert num_ways_split([10, 4, -8, 7]) == 2
    assert num_ways_split([2, 3, 1, 0]) == 2


def test_edges():
    assert num_ways_split([5]) == 0, "need two non-empty sides"
    assert num_ways_split([]) == 0
    assert num_ways_split([1, 1]) == 1


def test_random():
    rng = random.Random(6)
    for _ in range(200):
        nums = [rng.randint(-5, 5) for _ in range(rng.randint(0, 9))]
        want = sum(1 for i in range(len(nums) - 1) if sum(nums[:i + 1]) >= sum(nums[i + 1:]))
        assert num_ways_split(nums) == want, f"{nums}"
