# House robber

`nums[i]` is the money in house `i`. You cannot rob two **neighbouring** houses. Write `rob(nums)` that returns the most money you can take.

```python
rob([1, 2, 3, 1])      # -> 4
rob([2, 7, 9, 3, 1])   # -> 12
```

**Think first:** at house `i` you either skip it or rob it. What does each choice add?

**Hint:** pattern *1D DP (take or skip)*: `best[i] = max(best[i-1], best[i-2] + nums[i])`; two variables are enough.
