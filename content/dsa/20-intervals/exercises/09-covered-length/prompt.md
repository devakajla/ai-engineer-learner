# Total length covered by intervals

Intervals are `[start, end)`: they cover the numbers from `start` up to, but not including, `end` (length `end - start`). They can overlap. Write `covered_length(intervals)` that returns the total length covered by **at least one** interval (overlaps counted once).

```python
covered_length([[1, 3], [2, 5]])    # -> 4    (1 to 5)
covered_length([[1, 2], [2, 3]])    # -> 2
```

**Think first:** how is this different from adding up all the lengths? What do you do with the part that two intervals share?

**Hint:** pattern *sort + sweep*: sort by start, keep `reach` (the furthest end counted so far); add `max(0, end - max(start, reach))` for each interval and update `reach`.
