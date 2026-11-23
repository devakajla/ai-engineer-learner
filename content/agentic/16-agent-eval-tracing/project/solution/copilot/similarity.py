"""Compare vectors. Pure functions, no model calls."""

import numpy as np


def cosine_similarity(a, b):
    """Cosine of the angle between two vectors. A zero vector gives 0.0."""
    if len(a) != len(b):
        raise ValueError("vectors must have the same length")
    x = np.array(a, dtype=float)
    y = np.array(b, dtype=float)
    length_x = np.linalg.norm(x)
    length_y = np.linalg.norm(y)
    if length_x == 0 or length_y == 0:
        return 0.0
    return float(np.dot(x, y) / (length_x * length_y))


def cosine_scores(query_vector, doc_vectors):
    """One cosine score per document vector. A zero vector scores 0.0."""
    if len(doc_vectors) == 0:
        return []
    docs = np.array(doc_vectors, dtype=float)
    q = np.array(query_vector, dtype=float)
    lengths = np.linalg.norm(docs, axis=1) * np.linalg.norm(q)
    dots = docs @ q
    scores = np.zeros(len(docs))
    nonzero = lengths != 0
    scores[nonzero] = dots[nonzero] / lengths[nonzero]
    return [float(s) for s in scores]


def top_k(query_vector, doc_vectors, k):
    """The k best documents as (index, score) pairs, best first. Ties: lower index first."""
    if k <= 0 or len(doc_vectors) == 0:
        return []
    scores = cosine_scores(query_vector, doc_vectors)
    order = np.argsort(-np.array(scores), kind="stable")[:k]
    return [(int(i), scores[i]) for i in order]
