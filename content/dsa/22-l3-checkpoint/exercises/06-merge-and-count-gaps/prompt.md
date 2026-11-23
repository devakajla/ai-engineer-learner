# Merge intervals and count the gaps

Write `count_gaps(intervals)` that merges overlapping or touching closed intervals (real line: `[0, 1]` and `[2, 5]` are separate, `[1, 4]` and `[4, 5]` touch) `[start, end]` and returns how many **gaps** (empty spaces between merged intervals) there are.

```python
count_gaps([[1, 3], [2, 6], [8, 10], [15, 18]])    # -> 2
count_gaps([[1, 4], [4, 5]])                       # -> 0
```

**Think first:** how many gaps are there if the merged list has `m` intervals?

**Hint:** pattern *sort + merge*; the answer is `max(0, merged - 1)`.
