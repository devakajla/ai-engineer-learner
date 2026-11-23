import numpy as np


def cosine_similarity(a, b):
    if len(a) != len(b):
        raise ValueError("vectors must have the same length")
    x = np.array(a, dtype=float)
    y = np.array(b, dtype=float)
    length_x = np.linalg.norm(x)
    length_y = np.linalg.norm(y)
    if length_x == 0 or length_y == 0:
        return 0.0
    return float(np.dot(x, y) / (length_x * length_y))
