# Top k by cosine

Write `top_k(query, matrix, k)`. `query` is a list of numbers. `matrix` is a list of vectors (one per document). Return the `k` most similar documents as a list of `(index, score)` pairs, best first. `score` is the cosine similarity as a plain `float`.

Rules:
- Score every row of the matrix against the query with cosine similarity. A row (or query) with length 0 scores `0.0`.
- Sort best first. When two scores are equal, the **lower index** comes first.
- If `k` is bigger than the number of rows, return all rows. If `k <= 0` or the matrix is empty, return `[]`.
- Indexes must be plain Python `int`.

```python
matrix = [[1, 0], [0, 1], [1, 1]]
top_k([1, 0], matrix, 2)    # -> [(0, 1.0), (2, 0.7071067811865475)]
top_k([1, 0], matrix, 10)   # -> [(0, 1.0), (2, 0.7071067811865475), (1, 0.0)]
top_k([1, 0], [], 3)        # -> []
```

**Think first:** how can you score all rows without a loop in Python?

**Hint:** `matrix @ query`, `np.linalg.norm(matrix, axis=1)`, `np.argsort(-scores, kind="stable")`.
