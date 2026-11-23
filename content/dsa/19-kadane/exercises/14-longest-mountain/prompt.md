# Longest mountain

A **mountain** is a contiguous part of length at least 3 that goes **strictly up**, then **strictly down** (there must be both an up part and a down part). Write `longest_mountain(arr)` that returns the length of the longest mountain, or `0`.

```python
longest_mountain([2, 1, 4, 7, 3, 2, 5])    # -> 5    ([1, 4, 7, 3, 2])
longest_mountain([2, 2, 2])                # -> 0
```

**Think first:** for each possible peak, how far does the climb go on the left and how far on the right?

**Hint:** pattern *two streaks*: compute `up[i]` (length of the rising run ending at `i`) and `down[i]` (falling run starting at `i`). A peak has both `> 0`; length `up + down + 1`.
