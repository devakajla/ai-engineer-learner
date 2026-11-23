# Prepare the context

Models read the **start** and the **end** of a long context better than the **middle**. This is the "lost in the middle" problem. So put the best chunks at the two ends.

`dedupe_hits` (exercise 3) is in the starter. Write `prepare_context(hits, max_hits, max_per_source=2)`. `hits` come **best first**.

Rules:
1. If `max_hits <= 0`, return `[]`.
2. Remove repeats with `dedupe_hits(hits, max_per_source)`, then keep the first `max_hits`.
3. Reorder so the best are at the ends: first the hits at positions 0, 2, 4, ... in order, then the hits at positions 1, 3, 5, ... in **reverse** order.

For hits `h0 h1 h2 h3 h4` (best to worst) the result is `h0 h2 h4 h3 h1`: the best is first, the second best is last, and the weakest sits in the middle.

```python
prepare_context(hits_of_five_different_texts, max_hits=5)   # -> [h0, h2, h4, h3, h1]
prepare_context(hits, max_hits=2)                           # -> [h0, h1]
```

**Think first:** does reordering change what the model knows, or only how well it reads it?
