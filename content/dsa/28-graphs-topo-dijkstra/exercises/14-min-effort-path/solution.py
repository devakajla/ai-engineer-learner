import heapq


def min_effort(heights):
    rows, cols = len(heights), len(heights[0])
    best = {(0, 0): 0}
    heap = [(0, 0, 0)]
    while heap:
        effort, r, c = heapq.heappop(heap)
        if (r, c) == (rows - 1, cols - 1):
            return effort
        if effort > best[(r, c)]:
            continue
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < rows and 0 <= nc < cols:
                nxt = max(effort, abs(heights[nr][nc] - heights[r][c]))
                if nxt < best.get((nr, nc), float("inf")):
                    best[(nr, nc)] = nxt
                    heapq.heappush(heap, (nxt, nr, nc))
    return 0
