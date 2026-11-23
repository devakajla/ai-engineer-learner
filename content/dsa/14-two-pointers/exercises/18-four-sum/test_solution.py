import random
from itertools import combinations
from solution import four_sum


def brute(nums, target):
    return sorted(set(tuple(sorted(c)) for c in combinations(nums, 4) if sum(c) == target))


def test_examples():
    assert four_sum([1, 0, -1, 0, -2, 2], 0) == [[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]]
    assert four_sum([2, 2, 2, 2, 2], 8) == [[2, 2, 2, 2]]


def test_edges():
    assert four_sum([], 0) == []
    assert four_sum([1, 2, 3], 6) == []
    assert four_sum([0, 0, 0, 0], 1) == []
    assert four_sum([-3, -1, 0, 2, 4, 5], 2) == [[-3, -1, 2, 4]]


def test_random_against_brute_force():
    rng = random.Random(16)
    for _ in range(250):
        nums = [rng.randint(-4, 4) for _ in range(rng.randint(0, 9))]
        t = rng.randint(-6, 6)
        want = [list(q) for q in brute(nums, t)]
        assert four_sum(list(nums), t) == want, f"{nums}, {t}: expected {want}"
