def has_cycle_directed(n, edges):
    graph = {i: [] for i in range(n)}
    for a, b in edges:
        graph[a].append(b)
    state = [0] * n

    def visit(node):
        state[node] = 1
        for nb in graph[node]:
            if state[nb] == 1:
                return True
            if state[nb] == 0 and visit(nb):
                return True
        state[node] = 2
        return False

    return any(visit(s) for s in range(n) if state[s] == 0)
