from collections import deque


def shortest_path_len(n, edges, src, dst):
    graph = {i: [] for i in range(n)}
    for a, b in edges:
        graph[a].append(b)
        graph[b].append(a)
    dist = {src: 0}
    queue = deque([src])
    while queue:
        node = queue.popleft()
        for nb in graph[node]:
            if nb not in dist:
                dist[nb] = dist[node] + 1
                queue.append(nb)
    return dist.get(dst, -1)
