# nDCG@k

Sometimes chunks are right to different **degrees**: 3 = perfect, 2 = good, 1 = partly, 0 = wrong. **nDCG** (normalized discounted cumulative gain) rewards putting the best chunks first.

Write `ndcg_at_k(relevances, k)`. `relevances` holds the grade of each retrieved chunk, in the order the search returned them. `import math` is in the starter.

Rules:
- **DCG@k** = the sum over the first `k` positions of `grade / log2(position + 1)`. Positions count from 1.
- **Ideal DCG** is the DCG of the same grades sorted from best to worst (take the first `k`).
- Return `DCG / ideal DCG`. If the ideal DCG is 0 (no useful grade), return `0.0`.
- `k <= 0` gives `0.0`.

```python
ndcg_at_k([3, 2, 0], 3)            # -> 1.0               (already the best order)
ndcg_at_k([0, 2, 3], 3)            # -> 0.5972...         (best chunk is last)
ndcg_at_k([0, 0], 2)               # -> 0.0
```

**Think first:** why is dividing by `log2(position + 1)` a good way to punish a late rank?
