import random
from solution import has_cycle_undirected


def brute(n, edges):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x

    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra == rb:
            return True
        parent[ra] = rb
    return False


def test_examples():
    assert has_cycle_undirected(3, [[0, 1], [1, 2], [2, 0]]) is True
    assert has_cycle_undirected(4, [[0, 1], [1, 2]]) is False


def test_edges():
    assert has_cycle_undirected(0, []) is False
    assert has_cycle_undirected(2, [[0, 1]]) is False, "going back to the parent is not a cycle"


def test_random():
    rng = random.Random(9)
    for _ in range(300):
        n = rng.randint(1, 7)
        edges = [[a, b] for a in range(n) for b in range(a + 1, n) if rng.random() < 0.3]
        assert has_cycle_undirected(n, edges) is brute(n, edges), f"{n}, {edges}"
