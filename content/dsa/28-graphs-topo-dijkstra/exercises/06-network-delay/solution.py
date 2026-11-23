import heapq


def network_delay(times, n, k):
    graph = {i: [] for i in range(1, n + 1)}
    for u, v, w in times:
        graph[u].append((v, w))
    dist = {i: float("inf") for i in graph}
    dist[k] = 0
    heap = [(0, k)]
    while heap:
        d, node = heapq.heappop(heap)
        if d > dist[node]:
            continue
        for nb, w in graph[node]:
            if d + w < dist[nb]:
                dist[nb] = d + w
                heapq.heappush(heap, (dist[nb], nb))
    longest = max(dist.values())
    return -1 if longest == float("inf") else longest
