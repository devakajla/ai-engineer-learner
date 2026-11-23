import random
from solution import oranges_rotting


def brute(grid):
    g = [list(row) for row in grid]
    minutes = 0
    while True:
        if not any(1 in row for row in g):
            return minutes
        new = [list(row) for row in g]
        changed = False
        for r in range(len(g)):
            for c in range(len(g[0])):
                if g[r][c] == 1:
                    for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                        if 0 <= nr < len(g) and 0 <= nc < len(g[0]) and g[nr][nc] == 2:
                            new[r][c] = 2
                            changed = True
        if not changed:
            return -1
        g = new
        minutes += 1


def test_examples():
    assert oranges_rotting([[2, 1, 1], [1, 1, 0], [0, 1, 1]]) == 4
    assert oranges_rotting([[2, 1, 1], [0, 1, 1], [1, 0, 1]]) == -1


def test_edges():
    assert oranges_rotting([[0]]) == 0
    assert oranges_rotting([[1]]) == -1
    assert oranges_rotting([[2]]) == 0


def test_random():
    rng = random.Random(8)
    for _ in range(300):
        rows, cols = rng.randint(1, 4), rng.randint(1, 4)
        grid = [[rng.choice([0, 1, 1, 2]) for _ in range(cols)] for _ in range(rows)]
        copy = [list(r) for r in grid]
        assert oranges_rotting(grid) == brute(copy), f"{copy}"
