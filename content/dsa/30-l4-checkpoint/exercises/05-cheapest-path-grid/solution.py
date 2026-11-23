import heapq


def cheapest_path(grid):
    rows, cols = len(grid), len(grid[0])
    best = {(0, 0): grid[0][0]}
    heap = [(grid[0][0], 0, 0)]
    while heap:
        cost, r, c = heapq.heappop(heap)
        if (r, c) == (rows - 1, cols - 1):
            return cost
        if cost > best[(r, c)]:
            continue
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < rows and 0 <= nc < cols:
                nxt = cost + grid[nr][nc]
                if nxt < best.get((nr, nc), float("inf")):
                    best[(nr, nc)] = nxt
                    heapq.heappush(heap, (nxt, nr, nc))
    return -1
