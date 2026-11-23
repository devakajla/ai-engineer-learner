import random
from solution import region_sums


def brute(m, q):
    r1, c1, r2, c2 = q
    return sum(m[i][j] for i in range(r1, r2 + 1) for j in range(c1, c2 + 1))


def test_examples():
    m = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    assert region_sums(m, [[0, 0, 1, 1], [1, 1, 2, 2]]) == [12, 28]


def test_edges():
    assert region_sums([[5]], [[0, 0, 0, 0]]) == [5]
    m = [[1, -2], [3, 4]]
    assert region_sums(m, [[0, 0, 1, 1], [1, 0, 1, 0], [0, 1, 0, 1]]) == [6, 3, -2]


def test_random():
    rng = random.Random(15)
    for _ in range(100):
        r, c = rng.randint(1, 5), rng.randint(1, 5)
        m = [[rng.randint(-5, 5) for _ in range(c)] for _ in range(r)]
        qs = []
        for _ in range(5):
            r1 = rng.randint(0, r - 1)
            c1 = rng.randint(0, c - 1)
            qs.append([r1, c1, rng.randint(r1, r - 1), rng.randint(c1, c - 1)])
        assert region_sums(m, qs) == [brute(m, q) for q in qs], f"{m}, {qs}"
