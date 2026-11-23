def is_bipartite(graph):
    colour = {}
    for start in range(len(graph)):
        if start in colour:
            continue
        colour[start] = 0
        stack = [start]
        while stack:
            node = stack.pop()
            for nb in graph[node]:
                if nb not in colour:
                    colour[nb] = 1 - colour[node]
                    stack.append(nb)
                elif colour[nb] == colour[node]:
                    return False
    return True
