import random
from solution import kth_smallest


def test_examples():
    assert kth_smallest([[1, 5, 9], [10, 11, 13], [12, 13, 15]], 8) == 13
    assert kth_smallest([[-5]], 1) == -5


def test_edges():
    assert kth_smallest([[1, 2], [1, 3]], 2) == 1, "duplicates count separately"
    assert kth_smallest([[1, 2], [3, 4]], 4) == 4
    assert kth_smallest([[2, 2], [2, 2]], 3) == 2


def test_random():
    rng = random.Random(11)
    for _ in range(300):
        n = rng.randint(1, 5)
        m = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                up = m[i - 1][j] if i else 0
                left = m[i][j - 1] if j else 0
                m[i][j] = max(up, left) + rng.randint(0, 3)
        flat = sorted(x for row in m for x in row)
        k = rng.randint(1, n * n)
        assert kth_smallest(m, k) == flat[k - 1], f"{m}, {k}"
