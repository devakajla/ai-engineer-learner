# 3Sum closest

Write `three_sum_closest(nums, target)` (at least 3 numbers) that returns the **sum** of three numbers (different positions) closest to `target`. If two sums are equally close, return the **smaller** sum.

```python
three_sum_closest([-1, 2, 1, -4], 1)    # -> 2     (-1 + 2 + 1)
three_sum_closest([0, 0, 0], 1)         # -> 0
```

**Think first:** with sum `s` compared to `target`, which pointer do you move, and when do you stop early?

**Hint:** sort, fix `i`, two-end loop. Keep `best` and update it when `abs(s - target)` is smaller (or equal and `s` is smaller). If `s == target`, return it.
