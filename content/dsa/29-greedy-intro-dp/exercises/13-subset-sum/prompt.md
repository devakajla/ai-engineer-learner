# Subset sum

Write `can_make_sum(nums, target)` that returns `True` if some subset of `nums` (each number used at most once; the empty subset has sum 0) adds up to `target`. All numbers are `>= 0`.

```python
can_make_sum([3, 34, 4, 12, 5, 2], 9)    # -> True    (4 + 5)
can_make_sum([3, 34], 10)                # -> False
```

**Think first:** this is the knapsack question with a yes/no answer. What do you store for each sum?

**Hint:** pattern *boolean knapsack DP*: `ok[0] = True`; for each number loop `s` from `target` **down** to `num`: `ok[s] = ok[s] or ok[s - num]`.
