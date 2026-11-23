# Search with many queries

Search with every query, then merge the lists with **RRF** (lesson 18). `reciprocal_rank_fusion(rankings)` is in the starter: it takes a list of rankings (lists of ids) and returns `(id, score)` pairs, best first.

Write `retrieve_multi(retrieve, queries, k)`. `retrieve(query, k)` returns hits (dictionaries with an `"id"`).

Rules:
- For every query call `retrieve(query, k)`. Build one ranking of ids per query.
- Fuse the rankings with `reciprocal_rank_fusion`.
- Return the **hit dictionaries** of the top `k` fused ids, best first. If an id appears in several results, use the hit dictionary that was seen **first**.

```python
retrieve_multi(retrieve, ["delete a task", "remove a todo"], k=2)
# query 1 -> ids a, b     query 2 -> ids b, c
# fused: b (in both lists) comes first
# -> [hit_b, hit_a]
```

**Think first:** why does an id found by both queries rise to the top?
