# Remove a range from intervals

`intervals` is a sorted list of **non-overlapping** half-open intervals `[a, b)`. `remove` is also `[x, y)` with `x < y`. Write `remove_interval(intervals, remove)` that returns the intervals after cutting out the part covered by `remove`. An interval can be split in two. Leave out empty pieces.

```python
remove_interval([[0, 2], [3, 4], [5, 7]], [1, 6])    # -> [[0, 1], [6, 7]]
remove_interval([[0, 5]], [2, 3])                    # -> [[0, 2], [3, 5]]
```

**Think first:** for one interval `[a, b)`, what is left on the **left** of `remove` and what is left on the **right**?

**Hint:** pattern *interval arithmetic*: left piece is `[a, min(b, x))` if `a < min(b, x)`; right piece is `[max(a, y), b)` if `max(a, y) < b`.
