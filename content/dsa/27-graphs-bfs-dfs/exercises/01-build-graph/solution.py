def build_graph(n, edges):
    graph = {i: [] for i in range(n)}
    for a, b in edges:
        graph[a].append(b)
        graph[b].append(a)
    for node in graph:
        graph[node].sort()
    return graph
