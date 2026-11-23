import random
from solution import best_sightseeing


def brute(v):
    return max(v[i] + v[j] + i - j for i in range(len(v)) for j in range(i + 1, len(v)))


def test_examples():
    assert best_sightseeing([8, 1, 5, 2, 6]) == 11
    assert best_sightseeing([1, 2]) == 2


def test_edges():
    assert best_sightseeing([5, 5]) == 9
    assert best_sightseeing([1, 1, 1, 1]) == 1


def test_random():
    rng = random.Random(10)
    for _ in range(300):
        v = [rng.randint(1, 20) for _ in range(rng.randint(2, 10))]
        assert best_sightseeing(v) == brute(v), f"{v}"
