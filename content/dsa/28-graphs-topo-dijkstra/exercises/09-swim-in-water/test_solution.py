import random
from solution import swim_in_water


def reachable(grid, t):
    n = len(grid)
    if grid[0][0] > t:
        return False
    seen = {(0, 0)}
    stack = [(0, 0)]
    while stack:
        r, c = stack.pop()
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < n and 0 <= nc < n and (nr, nc) not in seen and grid[nr][nc] <= t:
                seen.add((nr, nc))
                stack.append((nr, nc))
    return (n - 1, n - 1) in seen


def brute(grid):
    t = 0
    while not reachable(grid, t):
        t += 1
    return t


def test_examples():
    assert swim_in_water([[0, 2], [1, 3]]) == 3
    assert swim_in_water([[0]]) == 0


def test_edges():
    assert swim_in_water([[3, 2], [0, 1]]) == 3, "the start cell counts too"


def test_random():
    rng = random.Random(9)
    for _ in range(300):
        n = rng.randint(1, 5)
        vals = list(range(n * n))
        rng.shuffle(vals)
        grid = [vals[i * n:(i + 1) * n] for i in range(n)]
        assert swim_in_water([list(r) for r in grid]) == brute(grid), f"{grid}"
