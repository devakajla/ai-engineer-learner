import random
from itertools import combinations
from solution import length_of_lis


def brute(nums):
    n = len(nums)
    best = 0
    for mask in range(1 << n):
        sub = [nums[i] for i in range(n) if mask >> i & 1]
        if all(sub[i] < sub[i + 1] for i in range(len(sub) - 1)):
            best = max(best, len(sub))
    return best


def test_examples():
    assert length_of_lis([10, 9, 2, 5, 3, 7, 101, 18]) == 4
    assert length_of_lis([7, 7, 7]) == 1


def test_edges():
    assert length_of_lis([]) == 0
    assert length_of_lis([1, 2, 3, 4]) == 4


def test_random():
    rng = random.Random(15)
    for _ in range(300):
        nums = [rng.randint(0, 6) for _ in range(rng.randint(0, 9))]
        assert length_of_lis(list(nums)) == brute(nums), f"{nums}"
