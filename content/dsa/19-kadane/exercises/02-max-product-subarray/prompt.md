# Maximum product subarray

Write `max_product(nums)` that returns the largest **product** of a non-empty contiguous part of `nums`. The list can have negatives and zeros.

```python
max_product([2, 3, -2, 4])    # -> 6
max_product([-2, 0, -1])      # -> 0
```

**Think first:** a very negative product can become the biggest after one more negative number. What second value must you remember besides the biggest product ending here?

**Hint:** pattern *Kadane with max and min*: keep `hi` and `lo` (biggest and smallest product ending here). For each `x`, new values come from `x`, `hi * x`, `lo * x`.
