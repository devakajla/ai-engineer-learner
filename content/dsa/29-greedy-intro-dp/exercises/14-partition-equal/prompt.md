# Split into two equal halves

Write `can_partition(nums)` that returns `True` if you can split `nums` into two groups with the **same sum**. All numbers are positive.

```python
can_partition([1, 5, 11, 5])    # -> True    ([1, 5, 5] and [11])
can_partition([1, 2, 3, 5])     # -> False
```

**Think first:** if the total is odd, is it possible? If it is even, what sum must one group have?

**Hint:** pattern *reduce to subset sum*: if `sum` is odd return `False`; else check for a subset with sum `total // 2` using the boolean knapsack from the last exercise.
