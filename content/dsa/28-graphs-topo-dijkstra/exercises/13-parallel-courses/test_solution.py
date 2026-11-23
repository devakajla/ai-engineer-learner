import random
from solution import min_semesters


def brute(n, relations):
    memo = {}
    visiting = set()

    def depth(c):
        if c in memo:
            return memo[c]
        if c in visiting:
            raise ValueError
        visiting.add(c)
        d = 1 + max([depth(a) for a, b in relations if b == c], default=0)
        visiting.discard(c)
        memo[c] = d
        return d

    try:
        return max(depth(c) for c in range(1, n + 1))
    except ValueError:
        return -1


def test_examples():
    assert min_semesters(3, [[1, 3], [2, 3]]) == 2
    assert min_semesters(3, [[1, 2], [2, 3], [3, 1]]) == -1


def test_edges():
    assert min_semesters(1, []) == 1
    assert min_semesters(4, []) == 1


def test_random():
    rng = random.Random(13)
    for _ in range(300):
        n = rng.randint(1, 6)
        relations = [[a, b] for a in range(1, n + 1) for b in range(1, n + 1) if a != b and rng.random() < 0.2]
        assert min_semesters(n, [list(r) for r in relations]) == brute(n, relations), f"{n}, {relations}"
