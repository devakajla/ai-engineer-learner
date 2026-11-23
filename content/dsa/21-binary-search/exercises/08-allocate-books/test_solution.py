import random
from itertools import combinations
from solution import allocate_books


def brute(pages, k):
    n = len(pages)
    best = None
    for cuts in combinations(range(1, n), k - 1):
        bounds = [0, *cuts, n]
        worst = max(sum(pages[a:b]) for a, b in zip(bounds, bounds[1:]))
        best = worst if best is None else min(best, worst)
    return best


def test_examples():
    assert allocate_books([12, 34, 67, 90], 2) == 113
    assert allocate_books([10, 20, 30], 3) == 30


def test_edges():
    assert allocate_books([5], 1) == 5
    assert allocate_books([1, 2, 3, 4], 1) == 10
    assert allocate_books([7, 2, 5, 10, 8], 2) == 18


def test_random():
    rng = random.Random(8)
    for _ in range(300):
        pages = [rng.randint(1, 15) for _ in range(rng.randint(1, 8))]
        k = rng.randint(1, len(pages))
        assert allocate_books(pages, k) == brute(pages, k), f"{pages}, {k}"
