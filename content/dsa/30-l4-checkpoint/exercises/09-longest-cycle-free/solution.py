def largest_group(n, friends):
    graph = {i: [] for i in range(n)}
    for a, b in friends:
        graph[a].append(b)
        graph[b].append(a)
    visited = set()
    best = 0
    for start in range(n):
        if start in visited:
            continue
        visited.add(start)
        stack = [start]
        size = 0
        while stack:
            node = stack.pop()
            size += 1
            for nb in graph[node]:
                if nb not in visited:
                    visited.add(nb)
                    stack.append(nb)
        best = max(best, size)
    return best
