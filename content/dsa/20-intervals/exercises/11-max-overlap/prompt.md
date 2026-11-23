# Maximum overlap at one point

Intervals are **closed integer** ranges `[start, end]` (both included). Write `max_overlap(intervals)` that returns the largest number of intervals that contain the same integer point. Return `0` for no intervals.

```python
max_overlap([[1, 4], [2, 5], [7, 9]])    # -> 2
max_overlap([[1, 3], [3, 5]])            # -> 2   (both contain 3)
```

**Think first:** turn each interval into two events: "+1 at start" and "-1 right after the end". What do you do with the running total?

**Hint:** pattern *sweep line*: events `(start, +1)` and `(end + 1, -1)`; sort them; with a running sum, the answer is its maximum. At equal times `-1` sorts before `+1`.
