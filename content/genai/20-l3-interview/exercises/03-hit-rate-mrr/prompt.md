# Hit rate and MRR

You tested a search on several questions. For each question you know the one chunk id that should be found. Write `retrieval_metrics(runs, k)`.

`runs` is a list of `(retrieved_ids, relevant_id)` pairs. `retrieved_ids` is the ranked result list, best first.

Return a dictionary with two floats:
- `"hit_rate"`: the share of runs where `relevant_id` is in the first `k` retrieved ids.
- `"mrr"`: the mean over all runs of `1 / rank`, where `rank` is the 1-based position of `relevant_id`, **only if it is in the first `k`**. Otherwise that run adds `0`.

Rules:
- No runs: both values are `0.0`.
- Raise `ValueError` if `k <= 0`.

```python
runs = [(["a", "b", "c"], "b"), (["x", "y", "z"], "q"), (["m", "n"], "m")]
retrieval_metrics(runs, 3)   # -> {'hit_rate': 0.6666..., 'mrr': 0.5}
retrieval_metrics(runs, 1)   # -> {'hit_rate': 0.3333..., 'mrr': 0.3333...}
retrieval_metrics([], 3)     # -> {'hit_rate': 0.0, 'mrr': 0.0}
```

With `k = 3`: run 1 is found at rank 2 (0.5), run 2 is not found (0), run 3 is found at rank 1 (1.0). Hit rate is 2/3. MRR is (0.5 + 0 + 1.0) / 3 = 0.5.

**Think first:** why does a result at rank 4 not count when `k = 3`, even if it is in the list?
