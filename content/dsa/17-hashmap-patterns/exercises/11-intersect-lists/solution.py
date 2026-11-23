def intersect(a, b):
    available = {}
    for x in a:
        available[x] = available.get(x, 0) + 1
    result = []
    for x in b:
        if available.get(x, 0) > 0:
            result.append(x)
            available[x] -= 1
    return sorted(result)
