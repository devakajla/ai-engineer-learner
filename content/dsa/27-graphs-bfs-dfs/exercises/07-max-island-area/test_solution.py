import random
from solution import max_island_area


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
    sizes = {}
    for label in cells.values():
        sizes[label] = sizes.get(label, 0) + 1
    return max(sizes.values(), default=0)


def test_examples():
    assert max_island_area(["11000", "11000", "00100", "00011"]) == 4
    assert max_island_area(["00"]) == 0


def test_edges():
    assert max_island_area([]) == 0
    assert max_island_area(["111", "111"]) == 6


def test_random():
    rng = random.Random(7)
    for _ in range(300):
        rows, cols = rng.randint(1, 5), rng.randint(1, 5)
        grid = ["".join(rng.choice("10") for _ in range(cols)) for _ in range(rows)]
        assert max_island_area(grid) == brute(grid), f"{grid}"
