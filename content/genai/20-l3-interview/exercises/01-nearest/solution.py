def cosine(a, b):
    length_a = sum(x * x for x in a) ** 0.5
    length_b = sum(x * x for x in b) ** 0.5
    if length_a == 0 or length_b == 0:
        return 0.0
    return sum(x * y for x, y in zip(a, b)) / (length_a * length_b)


def nearest(query, vectors, k):
    for vector in vectors:
        if len(vector) != len(query):
            raise ValueError("dimension mismatch")
    if k <= 0 or not vectors:
        return []
    pairs = [(-cosine(query, vector), i) for i, vector in enumerate(vectors)]
    pairs.sort()
    return [(i, float(-negative)) for negative, i in pairs[:k]]
