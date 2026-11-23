# Aggressive cows

`stalls` are positions on a line (not sorted, all different). Place `cows` cows in different stalls so that the **smallest distance between any two cows is as big as possible**. Write `max_min_distance(stalls, cows)` that returns that biggest possible smallest distance. `2 <= cows <= len(stalls)`.

```python
max_min_distance([1, 2, 4, 8, 9], 3)    # -> 3    (cows at 1, 4, 8 or 1, 4, 9)
max_min_distance([1, 2, 3], 2)          # -> 2
```

**Think first:** pick a distance `d`. Can you check, in one pass, whether `cows` cows fit with gaps of at least `d`? And if `d` works, does a smaller `d` work too?

**Hint:** pattern *binary search on the answer*: sort the stalls; `can_place(d)`: place the first cow at the first stall, then the next at the first stall `>= last + d`. Search `d` from `1` to `last - first`; if `can_place(mid)`, try bigger (`lo = mid + 1`).
