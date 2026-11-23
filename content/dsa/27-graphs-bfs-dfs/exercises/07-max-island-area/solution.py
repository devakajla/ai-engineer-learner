def max_island_area(grid):
    rows = len(grid)
    cols = len(grid[0]) if grid else 0
    visited = set()
    best = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != "1" or (r, c) in visited:
                continue
            visited.add((r, c))
            stack = [(r, c)]
            area = 0
            while stack:
                cr, cc = stack.pop()
                area += 1
                for nr, nc in ((cr + 1, cc), (cr - 1, cc), (cr, cc + 1), (cr, cc - 1)):
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == "1" and (nr, nc) not in visited:
                        visited.add((nr, nc))
                        stack.append((nr, nc))
            best = max(best, area)
    return best
