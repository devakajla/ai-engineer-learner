import numpy as np


def top_k(query, matrix, k):
    if k <= 0 or len(matrix) == 0:
        return []
    docs = np.array(matrix, dtype=float)
    q = np.array(query, dtype=float)
    lengths = np.linalg.norm(docs, axis=1) * np.linalg.norm(q)
    dots = docs @ q
    scores = np.zeros(len(docs))
    nonzero = lengths != 0
    scores[nonzero] = dots[nonzero] / lengths[nonzero]
    order = np.argsort(-scores, kind="stable")[:k]
    return [(int(i), float(scores[i])) for i in order]
