from itertools import combinations
from solution import combine


def test_examples():
    assert sorted(combine(4, 2)) == [[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]
    assert combine(3, 3) == [[1, 2, 3]]


def test_edges():
    assert combine(1, 1) == [[1]]
    assert combine(3, 0) == [[]]


def test_many():
    for n in range(1, 8):
        for k in range(0, n + 1):
            want = [list(c) for c in combinations(range(1, n + 1), k)]
            assert sorted(combine(n, k)) == want, f"n={n}, k={k}"
