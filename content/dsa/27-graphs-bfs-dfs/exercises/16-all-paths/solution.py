def all_paths(graph):
    target = len(graph) - 1
    result = []
    path = []

    def go(node):
        path.append(node)
        if node == target:
            result.append(list(path))
        else:
            for nb in graph[node]:
                go(nb)
        path.pop()

    go(0)
    return sorted(result)
