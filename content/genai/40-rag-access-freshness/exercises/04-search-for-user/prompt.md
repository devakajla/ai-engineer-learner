# A safe search

Put it together. In the starter: `allowed`, `filter_hits` and `drop_stale`.

Write `search_for_user(retrieve, user, question, k=3, today=None, max_age_days=None, overfetch=5)`.

Why `overfetch`? The user may not see many of the top hits. If you ask the search for only `k` hits and then remove some, you may be left with too few. So ask for **more** first.

Rules:
1. If `k <= 0`, return `[]`.
2. `hits = retrieve(question, k * overfetch)`.
3. Keep only the hits the user may see (`filter_hits`).
4. If both `today` and `max_age_days` are given (not `None`), also apply `drop_stale`.
5. Return the first `k` hits.

```python
search_for_user(retrieve, {"tenant": "acme", "groups": ["dev"]}, "how to pay?", k=2)
# retrieve is asked for 10 hits, the hits of other tenants and the hr-only chunks are removed,
# and the first 2 of the rest are returned
```

**Think first:** why must this filter run **before** the model sees the chunks, and not in the prompt?
