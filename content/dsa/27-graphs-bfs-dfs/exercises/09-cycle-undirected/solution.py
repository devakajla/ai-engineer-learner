def has_cycle_undirected(n, edges):
    graph = {i: [] for i in range(n)}
    for a, b in edges:
        graph[a].append(b)
        graph[b].append(a)
    visited = set()

    def visit(node, parent):
        visited.add(node)
        for nb in graph[node]:
            if nb == parent:
                continue
            if nb in visited or visit(nb, node):
                return True
        return False

    return any(visit(s, -1) for s in range(n) if s not in visited)
