import random
from itertools import combinations
from solution import min_largest_sum


def brute(nums, m):
    n = len(nums)
    best = sum(nums)
    for k in range(1, min(m, n) + 1):
        for cuts in combinations(range(1, n), k - 1):
            b = [0, *cuts, n]
            best = min(best, max(sum(nums[x:y]) for x, y in zip(b, b[1:])))
    return best


def test_examples():
    assert min_largest_sum([7, 2, 5, 10, 8], 2) == 18
    assert min_largest_sum([1, 2, 3], 5) == 3


def test_edges():
    assert min_largest_sum([4], 1) == 4
    assert min_largest_sum([1, 2, 3], 1) == 6


def test_random():
    rng = random.Random(8)
    for _ in range(300):
        nums = [rng.randint(1, 12) for _ in range(rng.randint(1, 7))]
        m = rng.randint(1, 5)
        assert min_largest_sum(nums, m) == brute(nums, m), f"{nums}, {m}"
