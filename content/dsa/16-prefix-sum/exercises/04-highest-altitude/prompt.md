# Highest altitude

A trip starts at altitude `0`. `gains[i]` is the change of altitude between point `i` and point `i + 1`. Write `max_altitude(gains)` that returns the highest altitude reached (the start counts).

```python
max_altitude([-5, 1, 5, 0, -7])             # -> 1
max_altitude([-4, -3, -2, -1, 4, 3, 2])     # -> 0
```

**Think first:** altitudes are exactly the prefix sums with a `0` in front.

**Hint:** pattern *prefix sum*: keep the running altitude and track its maximum, starting from `0`.
