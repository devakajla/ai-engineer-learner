import random
from solution import nearest_zero


def brute(mat):
    zeros = [(r, c) for r, row in enumerate(mat) for c, v in enumerate(row) if v == 0]
    return [[min(abs(r - zr) + abs(c - zc) for zr, zc in zeros) for c in range(len(mat[0]))] for r in range(len(mat))]


def test_examples():
    assert nearest_zero([[0, 0, 0], [0, 1, 0], [1, 1, 1]]) == [[0, 0, 0], [0, 1, 0], [1, 2, 1]]
    assert nearest_zero([[0]]) == [[0]]


def test_random():
    rng = random.Random(15)
    for _ in range(300):
        rows, cols = rng.randint(1, 5), rng.randint(1, 5)
        mat = [[rng.choice([0, 1, 1]) for _ in range(cols)] for _ in range(rows)]
        mat[rng.randrange(rows)][rng.randrange(cols)] = 0
        assert nearest_zero([list(r) for r in mat]) == brute(mat), f"{mat}"
