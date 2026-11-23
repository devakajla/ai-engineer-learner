import random
from itertools import combinations
from solution import triplets_smaller


def brute(nums, target):
    return sum(1 for c in combinations(nums, 3) if sum(c) < target)


def test_examples():
    assert triplets_smaller([-2, 0, 1, 3], 2) == 2
    assert triplets_smaller([1, 2], 5) == 0


def test_edges():
    assert triplets_smaller([], 0) == 0
    assert triplets_smaller([0, 0, 0], 0) == 0, "0 is not smaller than 0"
    assert triplets_smaller([0, 0, 0], 1) == 1
    assert triplets_smaller([3, 1, 0, -2], 4) == 3, "input is not sorted"


def test_random():
    rng = random.Random(8)
    for _ in range(250):
        nums = [rng.randint(-6, 6) for _ in range(rng.randint(0, 9))]
        t = rng.randint(-8, 8)
        assert triplets_smaller(list(nums), t) == brute(nums, t), f"{nums}, {t}"


def test_big_input_is_fast():
    nums = [(i * 31) % 997 for i in range(2500)]
    triplets_smaller(nums, 1500)
