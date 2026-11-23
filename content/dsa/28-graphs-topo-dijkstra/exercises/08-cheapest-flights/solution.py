def cheapest_price(n, flights, src, dst, k):
    inf = float("inf")
    dist = [inf] * n
    dist[src] = 0
    for _ in range(k + 1):
        nxt = list(dist)
        for u, v, price in flights:
            if dist[u] != inf and dist[u] + price < nxt[v]:
                nxt[v] = dist[u] + price
        dist = nxt
    return dist[dst] if dist[dst] != inf else -1
