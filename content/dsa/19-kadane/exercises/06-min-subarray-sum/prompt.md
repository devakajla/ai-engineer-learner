# Minimum subarray sum

Write `min_subarray(nums)` that returns the **smallest** sum of a non-empty contiguous part of `nums`.

```python
min_subarray([3, -4, 2, -3, -1, 7, -5])    # -> -6    ([-4, 2, -3, -1])
min_subarray([1, 2, 3])                    # -> 1
```

**Think first:** how does this change from the maximum version? Which `max` becomes `min`?

**Hint:** pattern *Kadane (min)*: `ending_here = min(x, ending_here + x)`; `best = min(best, ending_here)`.
