def dot(a, b):
    if len(a) != len(b):
        raise ValueError("vectors must have the same length")
    total = 0
    for x, y in zip(a, b):
        total += x * y
    return total
