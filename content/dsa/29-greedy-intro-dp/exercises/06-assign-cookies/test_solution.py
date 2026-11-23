import random
from solution import content_children


def brute(greed, sizes):
    best = 0
    # simple exact method: try all assignments of cookies to children or nobody
    def go(i, used, count):
        nonlocal best
        best = max(best, count)
        if i == len(sizes):
            return
        go(i + 1, used, count)
        for c in range(len(greed)):
            if c not in used and sizes[i] >= greed[c]:
                go(i + 1, used | {c}, count + 1)
    go(0, frozenset(), 0)
    return best


def test_examples():
    assert content_children([1, 2, 3], [1, 1]) == 1
    assert content_children([1, 2], [1, 2, 3]) == 2


def test_edges():
    assert content_children([], [1]) == 0
    assert content_children([1], []) == 0


def test_random():
    rng = random.Random(6)
    for _ in range(200):
        greed = [rng.randint(1, 5) for _ in range(rng.randint(0, 5))]
        sizes = [rng.randint(1, 5) for _ in range(rng.randint(0, 5))]
        assert content_children(list(greed), list(sizes)) == brute(greed, sizes), f"{greed}, {sizes}"
