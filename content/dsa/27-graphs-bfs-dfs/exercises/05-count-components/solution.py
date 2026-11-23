def count_components(n, edges):
    graph = {i: [] for i in range(n)}
    for a, b in edges:
        graph[a].append(b)
        graph[b].append(a)
    visited = set()
    count = 0
    for start in range(n):
        if start in visited:
            continue
        count += 1
        visited.add(start)
        stack = [start]
        while stack:
            node = stack.pop()
            for nb in graph[node]:
                if nb not in visited:
                    visited.add(nb)
                    stack.append(nb)
    return count
