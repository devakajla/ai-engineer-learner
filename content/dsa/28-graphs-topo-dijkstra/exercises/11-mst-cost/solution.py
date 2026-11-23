import heapq


def mst_cost(n, edges):
    graph = {i: [] for i in range(n)}
    for u, v, w in edges:
        graph[u].append((w, v))
        graph[v].append((w, u))
    in_tree = set()
    heap = [(0, 0)]
    total = 0
    while heap and len(in_tree) < n:
        w, node = heapq.heappop(heap)
        if node in in_tree:
            continue
        in_tree.add(node)
        total += w
        for item in graph[node]:
            if item[1] not in in_tree:
                heapq.heappush(heap, item)
    return total
