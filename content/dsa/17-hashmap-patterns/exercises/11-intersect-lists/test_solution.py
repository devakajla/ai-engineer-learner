import random
from solution import intersect


def brute(a, b):
    pool = list(b)
    out = []
    for x in a:
        if x in pool:
            pool.remove(x)
            out.append(x)
    return sorted(out)


def test_examples():
    assert intersect([1, 2, 2, 1], [2, 2]) == [2, 2]
    assert intersect([4, 9, 5], [9, 4, 9, 8, 4]) == [4, 9]


def test_edges():
    assert intersect([], [1]) == []
    assert intersect([1, 1, 1], [1]) == [1]
    assert intersect([1], [2]) == []


def test_random():
    rng = random.Random(11)
    for _ in range(300):
        a = [rng.randint(0, 4) for _ in range(rng.randint(0, 7))]
        b = [rng.randint(0, 4) for _ in range(rng.randint(0, 7))]
        assert intersect(a, b) == brute(a, b), f"{a}, {b}"
