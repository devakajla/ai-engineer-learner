import random
from solution import min_rooms


def brute(m):
    return max([sum(1 for s, e in m if s <= t < e) for t in range(0, 20)] or [0])


def test_examples():
    assert min_rooms([[0, 30], [5, 10], [15, 20]]) == 2
    assert min_rooms([[7, 10], [2, 4]]) == 1


def test_edges():
    assert min_rooms([]) == 0
    assert min_rooms([[1, 5], [5, 9]]) == 1


def test_random():
    rng = random.Random(14)
    for _ in range(300):
        m = []
        for _ in range(rng.randint(0, 7)):
            s = rng.randint(0, 12)
            m.append([s, s + rng.randint(1, 5)])
        assert min_rooms(m) == brute(m), f"{m}"
