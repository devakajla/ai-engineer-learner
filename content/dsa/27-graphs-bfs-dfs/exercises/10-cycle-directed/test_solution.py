import random
from solution import has_cycle_directed


def brute(n, edges):
    reach = [[False] * n for _ in range(n)]
    for a, b in edges:
        reach[a][b] = True
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if reach[i][k] and reach[k][j]:
                    reach[i][j] = True
    return any(reach[i][i] for i in range(n))


def test_examples():
    assert has_cycle_directed(3, [[0, 1], [1, 2], [2, 0]]) is True
    assert has_cycle_directed(3, [[0, 1], [0, 2], [1, 2]]) is False


def test_edges():
    assert has_cycle_directed(0, []) is False
    assert has_cycle_directed(1, [[0, 0]]) is True, "self loop"
    assert has_cycle_directed(2, [[0, 1], [1, 0]]) is True


def test_random():
    rng = random.Random(10)
    for _ in range(300):
        n = rng.randint(1, 6)
        edges = [[a, b] for a in range(n) for b in range(n) if a != b and rng.random() < 0.2]
        assert has_cycle_directed(n, edges) is brute(n, edges), f"{n}, {edges}"
