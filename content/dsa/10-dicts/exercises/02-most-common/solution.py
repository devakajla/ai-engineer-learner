def most_common(items):
    counts = {}
    for x in items:
        counts[x] = counts.get(x, 0) + 1
    best = items[0]
    for x in items:
        if counts[x] > counts[best]:
            best = x
    return best
