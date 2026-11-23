# Top K frequent numbers

Write `top_k_frequent(nums, k)` that returns the `k` most frequent numbers. Order: higher count first; for equal counts, the **smaller number** first. `k` is at most the number of different values.

```python
top_k_frequent([1, 1, 1, 2, 2, 3], 2)    # -> [1, 2]
top_k_frequent([4, 4, 5, 5, 6], 2)       # -> [4, 5]
```

**Think first:** first count (hashmap). Then which structure keeps the best `k` out of the counts?

**Hint:** pattern *count + heap of tuples*: `heapq.nsmallest(k, ((-count, value) for ...))` gives the right order; or push `(-count, value)` and pop `k` times.
