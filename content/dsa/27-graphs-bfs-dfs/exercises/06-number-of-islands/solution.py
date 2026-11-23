def num_islands(grid):
    rows = len(grid)
    cols = len(grid[0]) if grid else 0
    visited = set()
    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != "1" or (r, c) in visited:
                continue
            count += 1
            visited.add((r, c))
            stack = [(r, c)]
            while stack:
                cr, cc = stack.pop()
                for nr, nc in ((cr + 1, cc), (cr - 1, cc), (cr, cc + 1), (cr, cc - 1)):
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == "1" and (nr, nc) not in visited:
                        visited.add((nr, nc))
                        stack.append((nr, nc))
    return count
