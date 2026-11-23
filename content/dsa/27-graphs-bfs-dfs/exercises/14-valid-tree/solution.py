def valid_tree(n, edges):
    if len(edges) != n - 1:
        return False
    graph = {i: [] for i in range(n)}
    for a, b in edges:
        graph[a].append(b)
        graph[b].append(a)
    visited = {0} if n else set()
    stack = [0] if n else []
    while stack:
        node = stack.pop()
        for nb in graph[node]:
            if nb not in visited:
                visited.add(nb)
                stack.append(nb)
    return len(visited) == n
