# Reciprocal rank

Recall does not care about the **position** of the right chunk. But position matters: rank 1 is much better than rank 9. **Reciprocal rank** is `1 / rank` of the first right chunk. The average over many questions is the **MRR** (mean reciprocal rank).

Write `reciprocal_rank(expected_ids, retrieved_ids)`.

- Go through `retrieved_ids` from the start. Positions count from 1.
- At the first id that is in `expected_ids`, return `1 / position`.
- If none is found, return `0.0`.

```python
reciprocal_rank(["a"], ["a", "x"])        # -> 1.0
reciprocal_rank(["a"], ["x", "y", "a"])   # -> 0.3333333333333333
reciprocal_rank(["a"], ["x"])             # -> 0.0
```

Hint: `enumerate(items, start=1)` gives `(1, first)`, `(2, second)`, ...
