# Minimum meeting rooms with a heap

Same question as in the intervals lesson, solved with a heap. `meetings` is a list of `[start, end]` (end not included). Write `min_rooms(meetings)` that returns the fewest rooms needed.

```python
min_rooms([[0, 30], [5, 10], [15, 20]])    # -> 2
min_rooms([[7, 10], [2, 4]])               # -> 1
```

**Think first:** sort by start. For each meeting, which running meeting ends first? Can the new one use its room?

**Hint:** pattern *heap of end times*: for each meeting (sorted by start) if `h[0] <= start` pop it (room reused); push `end`. The answer is `len(h)` at the end.
