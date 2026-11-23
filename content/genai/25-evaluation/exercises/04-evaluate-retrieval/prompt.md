# Evaluate the whole search

Now score a search on a whole test set. In the starter: `recall_at_k`, `reciprocal_rank` and `precision_at_k` (exercises 1 to 3).

Write `evaluate_retrieval(retrieve, cases, k=5)`.

- `retrieve(question, k)` returns a list of hits, each a dictionary with an `"id"`.
- `cases` is a list of `{"question": ..., "expected": [ids]}`.

For every case: call `retrieve(question, k)`, take the ids in order, and compute recall@k, precision@k and the reciprocal rank.

Return a dictionary:
- `"n"`: number of cases.
- `"recall"`, `"precision"`, `"mrr"`: the **averages** over the cases, each rounded to 4 decimals.
- `"misses"`: the questions (in order) that have a non-empty `expected` list and recall of 0.0. Those are the retrieval misses to look at first.

With no cases return `{"n": 0, "recall": 0.0, "precision": 0.0, "mrr": 0.0, "misses": []}`.

```python
cases = [{"question": "q1", "expected": ["a"]}, {"question": "q2", "expected": ["b"]}]
# retrieve finds "a" at rank 1 for q1, and nothing right for q2
evaluate_retrieval(retrieve, cases, k=3)
# -> {'n': 2, 'recall': 0.5, 'precision': 0.1667, 'mrr': 0.5, 'misses': ['q2']}
```
