import random
from solution import dijkstra

INF = float("inf")


def brute(n, edges, src):
    d = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for u, v, w in edges:
        d[u][v] = min(d[u][v], w)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                d[i][j] = min(d[i][j], d[i][k] + d[k][j])
    return d[src]


def test_examples():
    assert dijkstra(3, [[0, 1, 4], [0, 2, 1], [2, 1, 2]], 0) == [0, 3, 1]
    assert dijkstra(2, [], 0) == [0, INF]


def test_edges():
    assert dijkstra(1, [], 0) == [0]
    assert dijkstra(2, [[0, 1, 0]], 0) == [0, 0], "weight 0 is allowed"


def test_random():
    rng = random.Random(5)
    for _ in range(300):
        n = rng.randint(1, 7)
        edges = [[a, b, rng.randint(0, 9)] for a in range(n) for b in range(n) if a != b and rng.random() < 0.3]
        src = rng.randrange(n)
        assert dijkstra(n, edges, src) == brute(n, edges, src), f"{n}, {edges}, {src}"
