import heapq


def max_capital(k, w, profits, capital):
    projects = sorted(zip(capital, profits))
    h = []
    i = 0
    for _ in range(k):
        while i < len(projects) and projects[i][0] <= w:
            heapq.heappush(h, -projects[i][1])
            i += 1
        if not h:
            break
        w += -heapq.heappop(h)
    return w
