import heapq


def max_probability(n, edges, probs, start, end):
    graph = {i: [] for i in range(n)}
    for (a, b), p in zip(edges, probs):
        graph[a].append((b, p))
        graph[b].append((a, p))
    best = [0.0] * n
    best[start] = 1.0
    heap = [(-1.0, start)]
    while heap:
        neg, node = heapq.heappop(heap)
        p = -neg
        if node == end:
            return p
        if p < best[node]:
            continue
        for nb, edge_p in graph[node]:
            if p * edge_p > best[nb]:
                best[nb] = p * edge_p
                heapq.heappush(heap, (-best[nb], nb))
    return 0.0
