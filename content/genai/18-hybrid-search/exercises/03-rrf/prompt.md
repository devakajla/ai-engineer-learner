# Reciprocal rank fusion

Write `reciprocal_rank_fusion(rankings, k=60)`. `rankings` is a list of ranked lists of ids, best first (for example one from vector search and one from keyword search).

For each id, the score is the sum of `1 / (k + rank)` over every list that contains it. The rank starts at **1**.

Return a list of `(id, score)` pairs, best score first. When scores are equal, the id seen **first** (looking through the lists in order, top to bottom) comes first.

Rules:
- An id appears at most once in each list. It may appear in several lists.
- No lists, or only empty lists, give `[]`.

```python
reciprocal_rank_fusion([["a", "b", "c"], ["c", "a", "d"]])
# -> [('a', 0.03252...), ('c', 0.03226...), ('b', 0.01612...), ('d', 0.01587...)]

reciprocal_rank_fusion([["x"], ["y"]], k=1)
# -> [('x', 0.5), ('y', 0.5)]        (tie: x was seen first)
```

**Think first:** how do you remember the order in which ids were first seen?

**Hint:** a dictionary `scores` (insertion order is kept), `enumerate(ranking, start=1)`, then `sorted(..., key=...)`. A sort is stable: equal keys keep their order. (If you have not met `key=` yet, use a loop to find the best, or ask Claude in the side panel.)
