import heapq


def min_rooms(meetings):
    h = []
    for start, end in sorted(meetings):
        if h and h[0] <= start:
            heapq.heappop(h)
        heapq.heappush(h, end)
    return len(h)
