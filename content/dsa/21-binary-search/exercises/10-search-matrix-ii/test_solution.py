import random
from solution import search_matrix_ii


def test_examples():
    m = [[1, 4, 7, 11], [2, 5, 8, 12], [3, 6, 9, 16], [10, 13, 14, 17]]
    assert search_matrix_ii(m, 5) is True
    assert search_matrix_ii(m, 15) is False


def test_edges():
    assert search_matrix_ii([], 1) is False
    assert search_matrix_ii([[]], 1) is False
    assert search_matrix_ii([[4]], 4) is True
    assert search_matrix_ii([[1, 2, 3]], 3) is True
    assert search_matrix_ii([[1], [2], [3]], 4) is False


def test_random():
    rng = random.Random(10)
    for _ in range(300):
        r, c = rng.randint(1, 5), rng.randint(1, 5)
        m = [[0] * c for _ in range(r)]
        for i in range(r):
            for j in range(c):
                up = m[i - 1][j] if i else 0
                left = m[i][j - 1] if j else 0
                m[i][j] = max(up, left) + rng.randint(1, 3)
        t = rng.randint(0, 25)
        assert search_matrix_ii(m, t) is any(t in row for row in m), f"{m}, {t}"
