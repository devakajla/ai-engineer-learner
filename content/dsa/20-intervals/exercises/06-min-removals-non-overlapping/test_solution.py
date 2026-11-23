import random
from itertools import combinations
from solution import min_removals


def ok(group):
    group = sorted(group)
    return all(group[i][0] >= group[i - 1][1] for i in range(1, len(group)))


def brute(iv):
    n = len(iv)
    for keep in range(n, -1, -1):
        for group in combinations(iv, keep):
            if ok(list(group)):
                return n - keep


def test_examples():
    assert min_removals([[1, 2], [2, 3], [3, 4], [1, 3]]) == 1
    assert min_removals([[1, 2], [1, 2], [1, 2]]) == 2


def test_edges():
    assert min_removals([]) == 0
    assert min_removals([[1, 2], [2, 3]]) == 0
    assert min_removals([[1, 100], [11, 22], [1, 11], [2, 12]]) == 2


def test_random():
    rng = random.Random(6)
    for _ in range(200):
        iv = []
        for _ in range(rng.randint(0, 6)):
            s = rng.randint(0, 8)
            iv.append([s, s + rng.randint(1, 4)])
        assert min_removals(iv) == brute(iv), f"{iv}"
