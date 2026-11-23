import heapq


def count_shortest_paths(n, edges):
    graph = {i: [] for i in range(n)}
    for u, v, w in edges:
        graph[u].append((v, w))
        graph[v].append((u, w))
    dist = [float("inf")] * n
    ways = [0] * n
    dist[0] = 0
    ways[0] = 1
    heap = [(0, 0)]
    while heap:
        d, node = heapq.heappop(heap)
        if d > dist[node]:
            continue
        for nb, w in graph[node]:
            if d + w < dist[nb]:
                dist[nb] = d + w
                ways[nb] = ways[node]
                heapq.heappush(heap, (dist[nb], nb))
            elif d + w == dist[nb]:
                ways[nb] += ways[node]
    return ways[n - 1]
