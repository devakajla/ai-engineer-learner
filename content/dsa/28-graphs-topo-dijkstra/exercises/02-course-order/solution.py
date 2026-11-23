from collections import deque


def find_order(n, prereqs):
    graph = {i: [] for i in range(n)}
    indegree = [0] * n
    for a, b in prereqs:
        graph[b].append(a)
        indegree[a] += 1
    queue = deque(i for i in range(n) if indegree[i] == 0)
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for nb in graph[node]:
            indegree[nb] -= 1
            if indegree[nb] == 0:
                queue.append(nb)
    return order if len(order) == n else []
