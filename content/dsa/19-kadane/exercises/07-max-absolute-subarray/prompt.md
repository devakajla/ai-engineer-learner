# Maximum absolute subarray sum

Write `max_abs_subarray(nums)` that returns the largest `abs(sum)` of any contiguous part. The part may be **empty** (sum 0), so the answer is never negative.

```python
max_abs_subarray([1, -3, 2, 3, -4])           # -> 5    ([2, 3] sums to 5)
max_abs_subarray([2, -5, 1, -4, 3, -2])       # -> 8    ([-5, 1, -4] sums to -8)
```

**Think first:** the biggest absolute value is either the biggest positive sum or the most negative sum. Can you get both in one pass?

**Hint:** pattern *Kadane, both directions*: run the max and the min version together, allowing the empty part (`max(0, ...)` / `min(0, ...)`). Answer `max(best_max, -best_min)`.
