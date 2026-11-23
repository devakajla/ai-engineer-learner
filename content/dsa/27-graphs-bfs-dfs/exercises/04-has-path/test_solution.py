import random
from solution import has_path


def brute(n, edges, s, t):
    reach = [[i == j for j in range(n)] for i in range(n)]
    for a, b in edges:
        reach[a][b] = reach[b][a] = True
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if reach[i][k] and reach[k][j]:
                    reach[i][j] = True
    return reach[s][t]


def test_examples():
    assert has_path(4, [[0, 1], [1, 2]], 0, 2) is True
    assert has_path(4, [[0, 1], [2, 3]], 0, 3) is False


def test_edges():
    assert has_path(1, [], 0, 0) is True


def test_random():
    rng = random.Random(4)
    for _ in range(300):
        n = rng.randint(1, 7)
        edges = [[a, b] for a in range(n) for b in range(a + 1, n) if rng.random() < 0.25]
        s, t = rng.randrange(n), rng.randrange(n)
        assert has_path(n, edges, s, t) is brute(n, edges, s, t), f"{n}, {edges}, {s}, {t}"
