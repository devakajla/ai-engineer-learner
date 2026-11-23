# K-th largest element

Write `kth_largest(nums, k)` that returns the k-th largest value (`k = 1` is the maximum; equal values count separately). `1 <= k <= len(nums)`. Use a heap of size `k`, not a full sort.

```python
kth_largest([3, 2, 1, 5, 6, 4], 2)           # -> 5
kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4)  # -> 4
```

**Think first:** keep only the `k` biggest numbers seen so far. Which one of them is the k-th largest?

**Hint:** pattern *min-heap of size k*: push each number; if `len(h) > k` pop the smallest. At the end `h[0]` is the answer.
