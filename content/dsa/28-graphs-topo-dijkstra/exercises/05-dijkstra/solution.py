import heapq


def dijkstra(n, edges, src):
    graph = {i: [] for i in range(n)}
    for u, v, w in edges:
        graph[u].append((v, w))
    dist = [float("inf")] * n
    dist[src] = 0
    heap = [(0, src)]
    while heap:
        d, node = heapq.heappop(heap)
        if d > dist[node]:
            continue
        for nb, w in graph[node]:
            if d + w < dist[nb]:
                dist[nb] = d + w
                heapq.heappush(heap, (dist[nb], nb))
    return dist
