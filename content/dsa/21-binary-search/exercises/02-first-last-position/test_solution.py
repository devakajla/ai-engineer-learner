import random
from solution import search_range


def brute(nums, t):
    idx = [i for i, x in enumerate(nums) if x == t]
    return [idx[0], idx[-1]] if idx else [-1, -1]


def test_examples():
    assert search_range([5, 7, 7, 8, 8, 10], 8) == [3, 4]
    assert search_range([5, 7, 7, 8, 8, 10], 6) == [-1, -1]


def test_edges():
    assert search_range([], 0) == [-1, -1]
    assert search_range([1], 1) == [0, 0]
    assert search_range([2, 2, 2, 2], 2) == [0, 3]
    assert search_range([1, 2, 3], 4) == [-1, -1]


def test_random():
    rng = random.Random(2)
    for _ in range(300):
        nums = sorted(rng.randint(0, 6) for _ in range(rng.randint(0, 12)))
        t = rng.randint(-1, 7)
        assert search_range(nums, t) == brute(nums, t), f"{nums}, {t}"
