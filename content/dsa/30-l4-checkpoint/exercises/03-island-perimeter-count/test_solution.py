import random
from solution import big_islands


def brute(grid, k):
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
    sizes = {}
    for label in cells.values():
        sizes[label] = sizes.get(label, 0) + 1
    return sum(1 for s in sizes.values() if s > k)


def test_examples():
    assert big_islands(["110", "110", "001"], 1) == 1
    assert big_islands(["101", "010", "101"], 0) == 5


def test_random():
    rng = random.Random(3)
    for _ in range(300):
        rows, cols = rng.randint(1, 5), rng.randint(1, 5)
        grid = ["".join(rng.choice("10") for _ in range(cols)) for _ in range(rows)]
        k = rng.randint(0, 4)
        assert big_islands(grid, k) == brute(grid, k), f"{grid}, {k}"
