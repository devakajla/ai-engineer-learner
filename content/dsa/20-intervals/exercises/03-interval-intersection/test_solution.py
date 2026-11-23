import random
from solution import interval_intersection


def brute(a, b):
    out = []
    for s1, e1 in a:
        for s2, e2 in b:
            lo, hi = max(s1, s2), min(e1, e2)
            if lo <= hi:
                out.append([lo, hi])
    return sorted(out)


def make(rng):
    cur, out = 0, []
    for _ in range(rng.randint(0, 4)):
        s = cur + rng.randint(1, 3)
        e = s + rng.randint(0, 3)
        out.append([s, e])
        cur = e
    return out


def test_examples():
    assert interval_intersection([[0, 2], [5, 10]], [[1, 5], [8, 12]]) == [[1, 2], [5, 5], [8, 10]]
    assert interval_intersection([[1, 3]], [[4, 5]]) == []


def test_edges():
    assert interval_intersection([], [[1, 2]]) == []
    assert interval_intersection([[1, 10]], [[2, 3], [5, 6]]) == [[2, 3], [5, 6]]
    assert interval_intersection([[1, 5]], [[5, 9]]) == [[5, 5]]


def test_random():
    rng = random.Random(3)
    for _ in range(300):
        a, b = make(rng), make(rng)
        assert interval_intersection(a, b) == brute(a, b), f"{a}, {b}"
