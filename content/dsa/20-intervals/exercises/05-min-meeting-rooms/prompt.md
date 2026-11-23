# Minimum meeting rooms

`meetings` is a list of `[start, end]` (end not included, so a room can be reused at `end`). Write `min_meeting_rooms(meetings)` that returns the smallest number of rooms needed so no two meetings in the same room overlap.

```python
min_meeting_rooms([[0, 30], [5, 10], [15, 20]])    # -> 2
min_meeting_rooms([[7, 10], [2, 4]])               # -> 1
```

**Think first:** you only need to know the **maximum number of meetings running at the same time**. Can you handle starts and ends in two separate sorted lists?

**Hint:** pattern *sweep with two sorted lists*: sort starts and ends; for each start, if it is `>=` the smallest unused end, a room frees up (move the end pointer), else you need one more room.
