def dfs_order(graph, start):
    visited = set()
    order = []

    def visit(node):
        visited.add(node)
        order.append(node)
        for nb in graph[node]:
            if nb not in visited:
                visit(nb)

    visit(start)
    return order
