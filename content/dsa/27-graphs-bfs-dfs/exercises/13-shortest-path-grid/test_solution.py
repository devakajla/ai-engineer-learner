import random
from solution import shortest_path


def brute(grid):
    rows, cols = len(grid), len(grid[0])
    if grid[0][0] == 1 or grid[-1][-1] == 1:
        return -1
    INF = 10 ** 9
    dist = [[INF] * cols for _ in range(rows)]
    dist[0][0] = 0
    for _ in range(rows * cols):
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == 0:
                    for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                        if 0 <= nr < rows and 0 <= nc < cols and dist[nr][nc] + 1 < dist[r][c]:
                            dist[r][c] = dist[nr][nc] + 1
    return dist[-1][-1] if dist[-1][-1] < INF else -1


def test_examples():
    assert shortest_path([[0, 0, 0], [1, 1, 0], [0, 0, 0]]) == 4
    assert shortest_path([[0, 1], [1, 0]]) == -1


def test_edges():
    assert shortest_path([[0]]) == 0
    assert shortest_path([[1]]) == -1
    assert shortest_path([[0, 1]]) == -1


def test_random():
    rng = random.Random(13)
    for _ in range(300):
        rows, cols = rng.randint(1, 5), rng.randint(1, 5)
        grid = [[1 if rng.random() < 0.3 else 0 for _ in range(cols)] for _ in range(rows)]
        assert shortest_path(grid) == brute(grid), f"{grid}"
