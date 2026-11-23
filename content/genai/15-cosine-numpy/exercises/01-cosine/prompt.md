# Cosine similarity

Write `cosine_similarity(a, b)` using numpy. `a` and `b` are lists of numbers.

Rules:
- If the lists have different lengths, raise `ValueError` with the message `"vectors must have the same length"`.
- If either vector has length 0 (all zeros), return `0.0`.
- Otherwise return `dot(a, b) / (length(a) * length(b))` as a plain Python `float`.

```python
cosine_similarity([1, 0], [1, 1])      # -> 0.7071067811865475
cosine_similarity([1, 1], [10, 10])    # -> 1.0
cosine_similarity([1, 0], [0, 1])      # -> 0.0
cosine_similarity([0, 0], [1, 2])      # -> 0.0
```

**Think first:** what two checks must come before the division?

**Hint:** `np.array(...)`, `np.dot(...)`, `np.linalg.norm(...)`.
