def euclidean(a, b):
    if len(a) != len(b):
        raise ValueError("vectors must have the same length")
    total = 0
    for x, y in zip(a, b):
        total += (x - y) ** 2
    return float(total ** 0.5)
