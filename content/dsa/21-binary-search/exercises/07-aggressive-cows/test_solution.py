import random
from itertools import combinations
from solution import max_min_distance


def brute(stalls, cows):
    best = 0
    for group in combinations(sorted(stalls), cows):
        best = max(best, min(b - a for a, b in zip(group, group[1:])))
    return best


def test_examples():
    assert max_min_distance([1, 2, 4, 8, 9], 3) == 3
    assert max_min_distance([1, 2, 3], 2) == 2


def test_edges():
    assert max_min_distance([5, 1], 2) == 4, "unsorted input"
    assert max_min_distance([1, 2, 3, 4], 4) == 1
    assert max_min_distance([10, 20, 30, 40, 50], 2) == 40


def test_random():
    rng = random.Random(7)
    for _ in range(300):
        stalls = rng.sample(range(0, 40), rng.randint(2, 8))
        cows = rng.randint(2, len(stalls))
        assert max_min_distance(stalls, cows) == brute(stalls, cows), f"{stalls}, {cows}"
