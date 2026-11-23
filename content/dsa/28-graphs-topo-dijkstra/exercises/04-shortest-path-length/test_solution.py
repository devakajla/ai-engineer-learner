import random
from solution import shortest_path_len


def brute(n, edges, s, t):
    INF = 10 ** 9
    d = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for a, b in edges:
        d[a][b] = d[b][a] = 1
    for k in range(n):
        for i in range(n):
            for j in range(n):
                d[i][j] = min(d[i][j], d[i][k] + d[k][j])
    return d[s][t] if d[s][t] < INF else -1


def test_examples():
    assert shortest_path_len(5, [[0, 1], [1, 2], [0, 3], [3, 2], [2, 4]], 0, 4) == 3
    assert shortest_path_len(3, [[0, 1]], 0, 2) == -1


def test_edges():
    assert shortest_path_len(1, [], 0, 0) == 0


def test_random():
    rng = random.Random(4)
    for _ in range(300):
        n = rng.randint(1, 7)
        edges = [[a, b] for a in range(n) for b in range(a + 1, n) if rng.random() < 0.25]
        s, t = rng.randrange(n), rng.randrange(n)
        assert shortest_path_len(n, edges, s, t) == brute(n, edges, s, t), f"{n}, {edges}, {s}, {t}"
