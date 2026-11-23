# Best subarray of exactly k items, or the best any-length subarray

Write `best_sums(nums, k)` that returns a pair `(best_window, best_any)`:
- `best_window`: the biggest sum of **exactly `k`** consecutive items,
- `best_any`: the biggest sum of **any non-empty** contiguous subarray.

Assume `1 <= k <= len(nums)`.

```python
best_sums([1, -2, 3, 4, -1], 2)    # -> (7, 7)
best_sums([-3, -1, -2], 2)         # -> (-3, -1)
```

**Think first:** these are two different patterns. Which one is a fixed-size window, and which one decides "extend or restart"?

**Hint:** patterns *fixed sliding window* and *Kadane*: `cur = max(n, cur + n)`.
