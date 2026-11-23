import random
from solution import search_matrix


def test_examples():
    m = [[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]]
    assert search_matrix(m, 3) is True
    assert search_matrix(m, 13) is False


def test_edges():
    assert search_matrix([], 1) is False
    assert search_matrix([[]], 1) is False
    assert search_matrix([[5]], 5) is True
    assert search_matrix([[1], [3]], 3) is True
    assert search_matrix([[1, 3]], 2) is False


def test_random():
    rng = random.Random(9)
    for _ in range(300):
        r, c = rng.randint(1, 4), rng.randint(1, 4)
        values = sorted(rng.sample(range(0, 40), r * c))
        m = [values[i * c:(i + 1) * c] for i in range(r)]
        t = rng.randint(-1, 41)
        assert search_matrix(m, t) is (t in values), f"{m}, {t}"
