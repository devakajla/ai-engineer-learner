import random
from solution import network_delay


def brute(times, n, k):
    INF = 10 ** 9
    d = [[0 if i == j else INF for j in range(n + 1)] for i in range(n + 1)]
    for u, v, w in times:
        d[u][v] = min(d[u][v], w)
    for m in range(1, n + 1):
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                d[i][j] = min(d[i][j], d[i][m] + d[m][j])
    worst = max(d[k][j] for j in range(1, n + 1))
    return -1 if worst >= INF else worst


def test_examples():
    assert network_delay([[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2) == 2
    assert network_delay([[1, 2, 1]], 2, 2) == -1


def test_edges():
    assert network_delay([], 1, 1) == 0


def test_random():
    rng = random.Random(6)
    for _ in range(300):
        n = rng.randint(1, 6)
        times = [[a, b, rng.randint(1, 9)] for a in range(1, n + 1) for b in range(1, n + 1) if a != b and rng.random() < 0.35]
        k = rng.randint(1, n)
        assert network_delay(times, n, k) == brute(times, n, k), f"{times}, {n}, {k}"
