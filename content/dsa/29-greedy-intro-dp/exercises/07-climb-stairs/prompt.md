# Climbing stairs

You climb `n` stairs taking 1 or 2 steps at a time. Write `climb_stairs(n)` that returns the number of different ways to reach the top.

```python
climb_stairs(3)    # -> 3    (1+1+1, 1+2, 2+1)
climb_stairs(1)    # -> 1
```

**Think first:** to stand on step `n`, which two steps could you have come from?

**Hint:** pattern *1D DP*: `ways[n] = ways[n-1] + ways[n-2]`; keep only the last two values.
