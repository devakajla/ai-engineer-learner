# Minimum start value

You pick a positive integer `start`. Then you add `nums[0]`, `nums[1]`, ... one by one. The running total must **never drop below 1**. Write `min_start_value(nums)` that returns the smallest positive `start` that works.

```python
min_start_value([-3, 2, -3, 4, 2])    # -> 5
min_start_value([1, 2])               # -> 1
```

**Think first:** which single prefix sum is the most dangerous?

**Hint:** pattern *prefix sum, minimum*: find the smallest prefix sum `low`. You need `start + low >= 1`, and `start >= 1`.
