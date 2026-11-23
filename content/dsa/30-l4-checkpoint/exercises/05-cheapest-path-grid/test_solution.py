import random
from solution import cheapest_path


def brute(grid):
    rows, cols = len(grid), len(grid[0])
    INF = 10 ** 9
    dist = [[INF] * cols for _ in range(rows)]
    dist[0][0] = grid[0][0]
    for _ in range(rows * cols):
        for r in range(rows):
            for c in range(cols):
                for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                    if 0 <= nr < rows and 0 <= nc < cols and dist[nr][nc] + grid[r][c] < dist[r][c]:
                        dist[r][c] = dist[nr][nc] + grid[r][c]
    return dist[-1][-1]


def test_examples():
    assert cheapest_path([[1, 3, 1], [1, 5, 1], [4, 2, 1]]) == 7
    assert cheapest_path([[5]]) == 5


def test_random():
    rng = random.Random(5)
    for _ in range(300):
        rows, cols = rng.randint(1, 5), rng.randint(1, 5)
        grid = [[rng.randint(1, 9) for _ in range(cols)] for _ in range(rows)]
        assert cheapest_path([list(r) for r in grid]) == brute(grid), f"{grid}"
