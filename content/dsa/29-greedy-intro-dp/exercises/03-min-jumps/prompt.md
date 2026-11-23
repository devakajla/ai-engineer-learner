# Fewest jumps to the end

Same jumps as before, and the end is always reachable. Write `min_jumps(nums)` that returns the fewest jumps needed to reach the last index.

```python
min_jumps([2, 3, 1, 1, 4])    # -> 2
min_jumps([0])                # -> 0
```

**Think first:** think of BFS rings: one jump reaches a range of indexes. When do you need one more jump?

**Hint:** pattern *greedy windows*: keep `end` (limit of the current jump) and `farthest`; when `i == end`, count a jump and set `end = farthest`.
