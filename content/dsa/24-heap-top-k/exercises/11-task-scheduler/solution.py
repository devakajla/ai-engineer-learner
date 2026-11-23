import heapq
from collections import deque


def least_interval(tasks, n):
    counts = {}
    for t in tasks:
        counts[t] = counts.get(t, 0) + 1
    h = [-c for c in counts.values()]
    heapq.heapify(h)
    waiting = deque()
    time = 0
    while h or waiting:
        time += 1
        if h:
            c = 1 + heapq.heappop(h)
            if c:
                waiting.append((c, time + n))
        if waiting and waiting[0][1] == time:
            heapq.heappush(h, waiting.popleft()[0])
    return time
