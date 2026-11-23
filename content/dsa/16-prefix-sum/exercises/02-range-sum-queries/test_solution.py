import random
from solution import range_sums


def test_examples():
    assert range_sums([2, 4, 1, 6, 3], [[0, 2], [1, 3], [4, 4]]) == [7, 11, 3]
    assert range_sums([5], [[0, 0]]) == [5]


def test_random():
    rng = random.Random(1)
    for _ in range(200):
        nums = [rng.randint(-9, 9) for _ in range(rng.randint(1, 12))]
        qs = []
        for _ in range(5):
            l = rng.randint(0, len(nums) - 1)
            qs.append([l, rng.randint(l, len(nums) - 1)])
        assert range_sums(nums, qs) == [sum(nums[l:r + 1]) for l, r in qs], f"{nums}, {qs}"


def test_empty_queries():
    assert range_sums([1, 2], []) == []
