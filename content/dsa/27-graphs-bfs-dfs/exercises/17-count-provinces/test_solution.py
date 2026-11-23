import random
from solution import count_provinces


def brute(m):
    n = len(m)
    reach = [[bool(m[i][j]) or i == j for j in range(n)] for i in range(n)]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if reach[i][k] and reach[k][j]:
                    reach[i][j] = True
    return len({tuple(row) for row in reach})


def test_examples():
    assert count_provinces([[1, 1, 0], [1, 1, 0], [0, 0, 1]]) == 2
    assert count_provinces([[1, 0], [0, 1]]) == 2


def test_edges():
    assert count_provinces([]) == 0
    assert count_provinces([[1]]) == 1


def test_random():
    rng = random.Random(17)
    for _ in range(300):
        n = rng.randint(0, 7)
        m = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                if rng.random() < 0.2:
                    m[i][j] = m[j][i] = 1
        assert count_provinces([list(r) for r in m]) == brute(m), f"{m}"
