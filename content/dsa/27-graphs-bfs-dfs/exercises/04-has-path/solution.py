def has_path(n, edges, src, dst):
    graph = {i: [] for i in range(n)}
    for a, b in edges:
        graph[a].append(b)
        graph[b].append(a)
    visited = {src}
    stack = [src]
    while stack:
        node = stack.pop()
        for nb in graph[node]:
            if nb not in visited:
                visited.add(nb)
                stack.append(nb)
    return dst in visited
