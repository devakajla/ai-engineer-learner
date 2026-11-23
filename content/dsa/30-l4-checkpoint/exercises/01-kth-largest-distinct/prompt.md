# K-th largest distinct value

Write `kth_largest_distinct(nums, k)` that returns the k-th largest **distinct** value, or `None` if there are fewer than `k` distinct values.

```python
kth_largest_distinct([3, 1, 3, 2, 2], 2)    # -> 2
kth_largest_distinct([5, 5], 2)             # -> None
```

**Think first:** which two tools do you combine: removing duplicates and picking the top k?

**Hint:** pattern *heap / top-k*: `set(nums)` then `heapq.nlargest(k, ...)`; check the length first.
