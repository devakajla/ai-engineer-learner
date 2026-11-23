# Remove the fewest intervals so none overlap

Intervals are `[start, end]`; two intervals that only touch (`end == start`) do **not** overlap. Write `min_removals(intervals)` that returns the smallest number of intervals to remove so the rest do not overlap.

```python
min_removals([[1, 2], [2, 3], [3, 4], [1, 3]])    # -> 1
min_removals([[1, 2], [1, 2], [1, 2]])            # -> 2
```

**Think first:** to keep as many as possible, which interval should you always keep first: the one that **starts** earliest or the one that **ends** earliest? Why?

**Hint:** pattern *greedy by end*: sort by end (use `sorted((end, start) ...)`), keep an interval if its start `>=` the end of the last kept one; otherwise count a removal.
