import random
from solution import k_closest


def test_examples():
    assert k_closest([[1, 3], [-2, 2]], 1) == [[-2, 2]]
    assert k_closest([[3, 3], [5, -1], [-2, 4]], 2) == [[3, 3], [-2, 4]]


def test_edges():
    assert k_closest([[0, 0]], 1) == [[0, 0]]
    assert k_closest([[1, 1], [-1, -1], [1, -1]], 3) == [[-1, -1], [1, -1], [1, 1]]


def test_random():
    rng = random.Random(5)
    for _ in range(200):
        pts = [[rng.randint(-5, 5), rng.randint(-5, 5)] for _ in range(rng.randint(1, 9))]
        k = rng.randint(1, len(pts))
        want = sorted(pts, key=lambda p: (p[0] ** 2 + p[1] ** 2, p[0], p[1]))[:k]
        assert k_closest([list(p) for p in pts], k) == want, f"{pts}, {k}"
