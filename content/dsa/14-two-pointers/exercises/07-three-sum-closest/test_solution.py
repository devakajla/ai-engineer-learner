import random
from itertools import combinations
from solution import three_sum_closest


def brute(nums, target):
    return min((sum(c) for c in combinations(nums, 3)), key=lambda s: (abs(s - target), s))


def test_examples():
    assert three_sum_closest([-1, 2, 1, -4], 1) == 2
    assert three_sum_closest([0, 0, 0], 1) == 0


def test_edges():
    assert three_sum_closest([1, 1, 1, 0], -100) == 2, "target far below everything"
    assert three_sum_closest([1, 1, 1, 0], 100) == 3, "target far above everything"
    assert three_sum_closest([1, 2, 5, 10, 11], 12) == 13
    assert three_sum_closest([0, 2, 4], 3) == 6


def test_tie_returns_smaller_sum():
    assert three_sum_closest([1, 1, 3, 3], 6) == 5, "sums 5 and 7 are both 1 away from 6; return 5"


def test_random():
    rng = random.Random(7)
    for _ in range(250):
        nums = [rng.randint(-10, 10) for _ in range(rng.randint(3, 8))]
        t = rng.randint(-15, 15)
        assert three_sum_closest(list(nums), t) == brute(nums, t), f"{nums}, {t}"
