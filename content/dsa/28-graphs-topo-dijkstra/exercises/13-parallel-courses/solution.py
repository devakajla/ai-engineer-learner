from collections import deque


def min_semesters(n, relations):
    graph = {i: [] for i in range(1, n + 1)}
    indegree = {i: 0 for i in range(1, n + 1)}
    for a, b in relations:
        graph[a].append(b)
        indegree[b] += 1
    queue = deque(i for i in graph if indegree[i] == 0)
    semesters = 0
    taken = 0
    while queue:
        semesters += 1
        for _ in range(len(queue)):
            node = queue.popleft()
            taken += 1
            for nb in graph[node]:
                indegree[nb] -= 1
                if indegree[nb] == 0:
                    queue.append(nb)
    return semesters if taken == n else -1
