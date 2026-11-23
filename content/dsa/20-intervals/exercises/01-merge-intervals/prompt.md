# Merge intervals

Each interval is `[start, end]` (closed). Write `merge_intervals(intervals)` that merges all intervals that **overlap or touch** (`[1, 4]` and `[4, 5]` become `[1, 5]`). The input is **not sorted**. Return the merged intervals sorted by start.

```python
merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]])    # -> [[1, 6], [8, 10], [15, 18]]
merge_intervals([[1, 4], [4, 5]])                       # -> [[1, 5]]
```

**Think first:** why does sorting by start make the job easy? Compare each interval only with the **last merged** one.

**Hint:** pattern *sort by start, then merge*: if `start <= merged[-1][1]` then `merged[-1][1] = max(merged[-1][1], end)`, else append a new interval.
