import random
from solution import count_gaps


def brute(iv):
    pts = sorted({x for s, e in iv for x in range(s * 2, e * 2 + 1)})
    return sum(1 for a, b in zip(pts, pts[1:]) if b - a > 1)


def test_examples():
    assert count_gaps([[1, 3], [2, 6], [8, 10], [15, 18]]) == 2
    assert count_gaps([[1, 4], [4, 5]]) == 0


def test_edges():
    assert count_gaps([]) == 0
    assert count_gaps([[1, 1]]) == 0
    assert count_gaps([[1, 2], [4, 5]]) == 1, "3 is missing"


def test_random():
    rng = random.Random(6)
    for _ in range(300):
        iv = []
        for _ in range(rng.randint(0, 6)):
            s = rng.randint(0, 15)
            iv.append([s, s + rng.randint(0, 3)])
        assert count_gaps([list(i) for i in iv]) == brute(iv), f"{iv}"
