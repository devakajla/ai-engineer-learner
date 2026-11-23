# Maximal marginal relevance (MMR)

A top-k of near-duplicate chunks wastes the prompt. **MMR** picks results that are relevant **and** different from each other.

Write `mmr(query_sims, doc_sims, k, lam=0.5)`.

- `query_sims[i]`: how similar document `i` is to the query.
- `doc_sims[i][j]`: how similar document `i` is to document `j` (a square list of lists).
- `lam`: between 0 and 1. `1.0` means only relevance, `0.0` means only diversity.

Pick `k` documents one by one. Each round, for every document not yet picked compute

```
mmr_score = lam * query_sims[i] - (1 - lam) * (the highest doc_sims[i][j] over the picked documents j)
```

and pick the one with the highest score. In the first round nothing is picked yet, so the penalty is `0`. Ties: the **lower index** wins.

Return the picked indexes, in the order they were picked.

Rules:
- If `k` is bigger than the number of documents, pick all of them. `k <= 0` or no documents give `[]`.

```python
query_sims = [0.9, 0.88, 0.5]
doc_sims = [[1.0, 0.95, 0.1],
            [0.95, 1.0, 0.1],
            [0.1, 0.1, 1.0]]
mmr(query_sims, doc_sims, 2, lam=1.0)   # -> [0, 1]   (only relevance)
mmr(query_sims, doc_sims, 2, lam=0.5)   # -> [0, 2]   (doc 1 is almost a copy of doc 0)
```

**Think first:** why is the penalty `0` in the first round? What does `max(..., default=0)` do?

**Hint:** keep a `picked` list and a `remaining` list. Use a loop inside a loop.
