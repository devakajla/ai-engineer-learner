import random
from solution import min_cost_ropes


def brute(r):
    if len(r) <= 1:
        return 0
    best = None
    for i in range(len(r)):
        for j in range(i + 1, len(r)):
            rest = [x for t, x in enumerate(r) if t not in (i, j)] + [r[i] + r[j]]
            c = r[i] + r[j] + brute(rest)
            best = c if best is None else min(best, c)
    return best


def test_examples():
    assert min_cost_ropes([4, 3, 2, 6]) == 29
    assert min_cost_ropes([1, 2, 3]) == 9


def test_edges():
    assert min_cost_ropes([]) == 0
    assert min_cost_ropes([5]) == 0


def test_random():
    rng = random.Random(8)
    for _ in range(100):
        r = [rng.randint(1, 9) for _ in range(rng.randint(0, 5))]
        assert min_cost_ropes(list(r)) == brute(r), f"{r}"
