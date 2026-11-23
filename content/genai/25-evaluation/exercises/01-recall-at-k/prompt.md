# Recall at k

**Recall@k** asks: of the chunks that **should** be found, how many are in the top `k` results? It is the most important retrieval number. If the right chunk is not in the top `k`, the model never sees it.

Write `recall_at_k(expected_ids, retrieved_ids, k)`.

- `expected_ids`: ids of the chunks that hold the answer.
- `retrieved_ids`: ids the search returned, best first.
- Look only at the first `k` of `retrieved_ids`.
- Return `found / len(expected_ids)`, a number from 0 to 1.
- If `expected_ids` is empty (nothing to find), return `1.0`.
- If `k <= 0`, nothing is looked at.

```python
recall_at_k(["a", "b"], ["x", "a", "y"], 3)   # -> 0.5
recall_at_k(["a"], ["x", "a"], 1)             # -> 0.0   (a is at position 2, outside the top 1)
recall_at_k([], ["x"], 3)                     # -> 1.0
```
