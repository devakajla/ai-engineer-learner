from collections import deque


def shortest_path(grid):
    rows, cols = len(grid), len(grid[0])
    if grid[0][0] == 1 or grid[rows - 1][cols - 1] == 1:
        return -1
    visited = {(0, 0)}
    queue = deque([(0, 0, 0)])
    while queue:
        r, c, steps = queue.popleft()
        if (r, c) == (rows - 1, cols - 1):
            return steps
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0 and (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append((nr, nc, steps + 1))
    return -1
