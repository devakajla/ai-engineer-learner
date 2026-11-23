import random
from solution import bellman_ford

INF = float("inf")


def brute(n, edges, src):
    d = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for u, v, w in edges:
        d[u][v] = min(d[u][v], w)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if d[i][k] + d[k][j] < d[i][j]:
                    d[i][j] = d[i][k] + d[k][j]
    for v in range(n):
        if d[src][v] < INF and d[v][v] < 0:
            return None
    return [d[src][v] for v in range(n)]


def test_examples():
    assert bellman_ford(3, [[0, 1, 4], [0, 2, 5], [1, 2, -3]], 0) == [0, 4, 1]
    assert bellman_ford(2, [[0, 1, 1], [1, 0, -2]], 0) is None


def test_edges():
    assert bellman_ford(1, [], 0) == [0]
    assert bellman_ford(3, [[1, 2, -5], [2, 1, 1]], 0) == [0, INF, INF], "negative cycle not reachable from src"


def test_random():
    rng = random.Random(7)
    for _ in range(300):
        n = rng.randint(1, 5)
        edges = [[a, b, rng.randint(-3, 8)] for a in range(n) for b in range(n) if a != b and rng.random() < 0.3]
        src = rng.randrange(n)
        assert bellman_ford(n, [list(e) for e in edges], src) == brute(n, edges, src), f"{n}, {edges}, {src}"
