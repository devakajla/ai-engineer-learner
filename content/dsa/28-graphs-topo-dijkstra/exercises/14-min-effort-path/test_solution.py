import random
from solution import min_effort


def reachable(h, limit):
    rows, cols = len(h), len(h[0])
    seen = {(0, 0)}
    stack = [(0, 0)]
    while stack:
        r, c = stack.pop()
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in seen and abs(h[nr][nc] - h[r][c]) <= limit:
                seen.add((nr, nc))
                stack.append((nr, nc))
    return (rows - 1, cols - 1) in seen


def brute(h):
    limit = 0
    while not reachable(h, limit):
        limit += 1
    return limit


def test_examples():
    assert min_effort([[1, 2, 2], [3, 8, 2], [5, 3, 5]]) == 2
    assert min_effort([[1, 10], [10, 1]]) == 9


def test_edges():
    assert min_effort([[5]]) == 0
    assert min_effort([[1, 4, 2]]) == 3


def test_random():
    rng = random.Random(14)
    for _ in range(300):
        rows, cols = rng.randint(1, 4), rng.randint(1, 4)
        h = [[rng.randint(0, 9) for _ in range(cols)] for _ in range(rows)]
        assert min_effort([list(r) for r in h]) == brute(h), f"{h}"
