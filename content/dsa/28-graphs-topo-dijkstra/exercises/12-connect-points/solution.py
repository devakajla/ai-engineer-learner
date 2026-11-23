def min_cost_connect(points):
    n = len(points)
    best = [float("inf")] * n
    best[0] = 0
    done = [False] * n
    total = 0
    for _ in range(n):
        node = min((i for i in range(n) if not done[i]), key=best.__getitem__)
        done[node] = True
        total += best[node]
        for other in range(n):
            if not done[other]:
                d = abs(points[node][0] - points[other][0]) + abs(points[node][1] - points[other][1])
                if d < best[other]:
                    best[other] = d
    return total
