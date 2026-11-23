def intersect_counts(a, b):
    counts = {}
    for x in a:
        counts[x] = counts.get(x, 0) + 1
    result = []
    for x in b:
        if counts.get(x, 0) > 0:
            result.append(x)
            counts[x] -= 1
    return sorted(result)
