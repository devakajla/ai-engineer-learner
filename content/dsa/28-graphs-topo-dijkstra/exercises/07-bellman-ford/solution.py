def bellman_ford(n, edges, src):
    inf = float("inf")
    dist = [inf] * n
    dist[src] = 0
    for _ in range(n - 1):
        for u, v, w in edges:
            if dist[u] != inf and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    for u, v, w in edges:
        if dist[u] != inf and dist[u] + w < dist[v]:
            return None
    return dist
