# Free gaps in a day

Meetings are `[start, end)` and can overlap. The day runs from `lo` to `hi` (`lo < hi`). Write `free_gaps(meetings, lo, hi)` that returns the free time slots `[a, b)` inside the day (not covered by any meeting), sorted. Parts of meetings outside `[lo, hi)` are ignored. Leave out empty slots.

```python
free_gaps([[9, 11], [10, 12], [14, 15]], 8, 17)    # -> [[8, 9], [12, 14], [15, 17]]
free_gaps([], 8, 10)                                # -> [[8, 10]]
```

**Think first:** walk through the sorted meetings with a pointer `cursor` that means "free from here on". When is there a gap before the next meeting?

**Hint:** pattern *sort + sweep with a cursor*: if `start > cursor`, the slot `[cursor, start)` is free; then `cursor = max(cursor, end)`. Do not forget the slot after the last meeting.
