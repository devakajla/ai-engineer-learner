# K smallest pair sums

`a` and `b` are sorted lists. A pair is one number from each list. Write `k_smallest_pairs(a, b, k)` that returns the `k` pairs `[x, y]` with the smallest sums. Order: smaller sum first, then smaller `x`, then smaller `y`. If there are fewer than `k` pairs, return all.

```python
k_smallest_pairs([1, 7, 11], [2, 4, 6], 3)    # -> [[1, 2], [1, 4], [1, 6]]
k_smallest_pairs([1, 1, 2], [1, 2, 3], 2)     # -> [[1, 1], [1, 1]]
```

**Think first:** you do not want all `len(a) * len(b)` pairs. After you take pair `(i, j)`, which pair becomes the next candidate in that row?

**Hint:** pattern *heap as a frontier*: start with `(a[i] + b[0], i, 0)` for the first `min(k, len(a))` values of `i`; after popping `(s, i, j)` push `(a[i] + b[j + 1], i, j + 1)`.
