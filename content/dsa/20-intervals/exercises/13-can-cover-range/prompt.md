# Can the intervals cover a range?

Intervals are **closed integer** ranges `[start, end]`. Write `can_cover(intervals, lo, hi)` that returns `True` if **every integer** from `lo` to `hi` (both included) lies in at least one interval.

```python
can_cover([[1, 3], [4, 6]], 1, 6)    # -> True   (3 and 4 are neighbours)
can_cover([[1, 3], [5, 6]], 1, 6)    # -> False  (4 is missing)
```

**Think first:** keep `next_needed`: the smallest number not covered yet. Which interval can move it forward?

**Hint:** pattern *sort + greedy reach*: sort by start; if an interval starts `<= next_needed`, set `next_needed = max(next_needed, end + 1)`; if it starts later, there is a hole. Done when `next_needed > hi`.
