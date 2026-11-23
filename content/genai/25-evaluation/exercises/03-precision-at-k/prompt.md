# Precision at k

**Precision@k** asks: of the `k` results, how many are right? High precision means little noise in the prompt.

Write `precision_at_k(expected_ids, retrieved_ids, k)`.

- Look at the first `k` ids of `retrieved_ids`.
- Count how many are in `expected_ids`.
- Return `count / k`. Always divide by `k`, even if fewer than `k` results came back (missing results count as wrong).
- If `k <= 0`, return `0.0`.

```python
precision_at_k(["a", "b"], ["a", "x", "b"], 3)   # -> 0.6666666666666666
precision_at_k(["a"], ["a"], 4)                   # -> 0.25
precision_at_k(["a"], ["a"], 0)                   # -> 0.0
```

**Think first:** why can recall be 1.0 while precision is low?
