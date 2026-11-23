# Can you attend all meetings?

`meetings` is a list of `[start, end]`. A meeting uses the time from `start` up to (but not including) `end`, so one meeting can start exactly when another ends. Write `can_attend_all(meetings)` that returns `True` if no two meetings overlap.

```python
can_attend_all([[0, 30], [5, 10], [15, 20]])    # -> False
can_attend_all([[7, 10], [2, 4]])               # -> True
```

**Think first:** after sorting by start time, which pairs do you need to compare?

**Hint:** pattern *sort + neighbours*: after sorting, any overlap shows up between two **neighbours**: `meetings[i][0] < meetings[i - 1][1]`.
