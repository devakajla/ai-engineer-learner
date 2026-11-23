import random
from solution import valid_tree


def brute(n, edges):
    if n == 0:
        return False
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x

    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra == rb:
            return False
        parent[ra] = rb
    return len({find(i) for i in range(n)}) == 1


def test_examples():
    assert valid_tree(5, [[0, 1], [0, 2], [0, 3], [1, 4]]) is True
    assert valid_tree(5, [[0, 1], [1, 2], [2, 3], [1, 3], [1, 4]]) is False


def test_edges():
    assert valid_tree(1, []) is True
    assert valid_tree(2, []) is False, "not connected"


def test_random():
    rng = random.Random(14)
    for _ in range(300):
        n = rng.randint(1, 7)
        edges = [[a, b] for a in range(n) for b in range(a + 1, n) if rng.random() < 0.3]
        assert valid_tree(n, edges) is brute(n, edges), f"{n}, {edges}"
