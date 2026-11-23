import random
from solution import free_gaps


def brute(meetings, lo, hi):
    free = [all(not (s <= t < e) for s, e in meetings) for t in range(lo, hi)]
    out = []
    for i, f in enumerate(free):
        t = lo + i
        if f:
            if out and out[-1][1] == t:
                out[-1][1] = t + 1
            else:
                out.append([t, t + 1])
    return out


def test_examples():
    assert free_gaps([[9, 11], [10, 12], [14, 15]], 8, 17) == [[8, 9], [12, 14], [15, 17]]
    assert free_gaps([], 8, 10) == [[8, 10]]


def test_edges():
    assert free_gaps([[0, 20]], 8, 10) == []
    assert free_gaps([[1, 3]], 8, 10) == [[8, 10]], "meeting before the day"
    assert free_gaps([[8, 9], [9, 10]], 8, 10) == []
    assert free_gaps([[12, 14]], 8, 10) == [[8, 10]], "meeting after the day"


def test_random():
    rng = random.Random(12)
    for _ in range(300):
        m = []
        for _ in range(rng.randint(0, 5)):
            s = rng.randint(0, 14)
            m.append([s, s + rng.randint(1, 5)])
        lo = rng.randint(0, 6)
        hi = lo + rng.randint(1, 10)
        assert free_gaps(m, lo, hi) == brute(m, lo, hi), f"{m}, {lo}, {hi}"
