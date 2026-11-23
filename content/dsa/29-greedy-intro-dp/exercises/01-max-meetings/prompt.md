# Most meetings in one room

`meetings` is a list of `[start, end]`. One room, no overlap allowed (a meeting may start exactly when another ends). Write `max_meetings(meetings)` that returns the largest number of meetings you can hold.

```python
max_meetings([[1, 3], [2, 4], [3, 5]])    # -> 2
max_meetings([])                          # -> 0
```

**Think first:** which meeting should you pick first, the one that starts first or the one that ends first?

**Hint:** pattern *greedy: earliest finish*: sort by end time (sort `(end, start)` pairs); take a meeting if its start is `>=` the end of the last taken one.
