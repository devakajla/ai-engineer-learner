import random
from solution import num_islands


def brute(grid):
    cells = {(r, c): (r, c) for r, row in enumerate(grid) for c, ch in enumerate(row) if ch == "1"}
    changed = True
    while changed:
        changed = False
        for (r, c) in cells:
            for nb in ((r + 1, c), (r, c + 1)):
                if nb in cells:
                    m = min(cells[(r, c)], cells[nb])
                    if cells[(r, c)] != m or cells[nb] != m:
                        cells[(r, c)] = cells[nb] = m
                        changed = True
    return len(set(cells.values()))


def test_examples():
    assert num_islands(["11000", "11000", "00100", "00011"]) == 3
    assert num_islands(["000"]) == 0


def test_edges():
    assert num_islands([]) == 0
    assert num_islands(["1"]) == 1
    assert num_islands(["101", "010", "101"]) == 5, "diagonals do not connect"


def test_random():
    rng = random.Random(6)
    for _ in range(300):
        rows, cols = rng.randint(1, 5), rng.randint(1, 5)
        grid = ["".join(rng.choice("10") for _ in range(cols)) for _ in range(rows)]
        assert num_islands(grid) == brute(grid), f"{grid}"
