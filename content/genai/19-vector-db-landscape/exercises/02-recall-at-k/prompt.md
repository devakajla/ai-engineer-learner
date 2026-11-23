# Recall at k

Write `recall_at_k(found, truth, k)`. `truth` is the list of the real nearest ids (from exact search), best first. `found` is what an approximate index returned, best first.

Recall@k is: how many of the true top `k` ids are inside the first `k` ids of `found`, divided by the size of the true top `k`.

Rules:
- Use `truth[:k]` and `found[:k]`. Order inside the lists does not matter for the count.
- If `truth[:k]` is empty (no true neighbours), return `1.0`: there was nothing to miss.
- Raise `ValueError` if `k <= 0`.
- Return a float.

```python
recall_at_k(["a", "c", "x", "d"], ["a", "b", "c", "d"], 4)   # -> 0.75
recall_at_k(["a", "b"], ["a", "b", "c"], 2)                  # -> 1.0
recall_at_k(["x", "y"], ["a", "b"], 2)                       # -> 0.0
recall_at_k(["a"], [], 3)                                    # -> 1.0
```

**Think first:** why do we cut `found` to `k` items too?
