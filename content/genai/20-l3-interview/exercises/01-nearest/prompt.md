# Nearest neighbours in pure Python

Write `nearest(query, vectors, k)` **without numpy**. Return the `k` vectors most similar to `query` by cosine similarity, as a list of `(index, score)` pairs, best first.

Rules:
- Cosine similarity = `dot(a, b) / (length(a) * length(b))`. If either length is 0, the score is `0.0`.
- Ties: the **lower index** comes first.
- If any vector has a different length from the query, raise `ValueError("dimension mismatch")`.
- `k <= 0` or no vectors give `[]`. A `k` bigger than the count returns all.
- Scores are plain floats.

```python
nearest([1, 0], [[1, 0], [0, 1], [1, 1]], 2)
# -> [(0, 1.0), (2, 0.7071067811865475)]
nearest([1, 0], [[0, 0], [2, 0]], 5)
# -> [(1, 1.0), (0, 0.0)]
nearest([1, 0], [[1, 0, 0]], 1)     # raises ValueError
```

**Think first:** how can a sort give "best first, ties by lower index"?

**Hint:** sort a list of `(-score, index)` pairs.
