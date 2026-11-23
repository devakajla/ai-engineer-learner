# Combinations n choose k

Write `combine(n, k)` that returns all combinations of `k` numbers chosen from `1..n`. Each combination is a list in increasing order. Any order of results.

```python
combine(4, 2)    # -> [[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]   (any order)
combine(3, 3)    # -> [[1, 2, 3]]
```

**Think first:** if you choose number `i`, which numbers may come after it? How can you stop early when too few numbers are left?

**Hint:** pattern *choose from a start index*: `go(start)`: for `i` in `start..n`: append `i`, `go(i + 1)`, pop. Save when `len(current) == k`.
