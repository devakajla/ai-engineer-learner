import random
from itertools import combinations
from solution import count_zero_triplets


def brute(nums):
    return len({tuple(sorted(c)) for c in combinations(nums, 3) if sum(c) == 0})


def test_examples():
    assert count_zero_triplets([-1, 0, 1, 2, -1, -4]) == 2
    assert count_zero_triplets([0, 0, 0, 0]) == 1


def test_edges():
    assert count_zero_triplets([]) == 0
    assert count_zero_triplets([0, 0]) == 0
    assert count_zero_triplets([1, 2, 3]) == 0


def test_random():
    rng = random.Random(1)
    for _ in range(300):
        nums = [rng.randint(-4, 4) for _ in range(rng.randint(0, 9))]
        assert count_zero_triplets(list(nums)) == brute(nums), f"{nums}"
