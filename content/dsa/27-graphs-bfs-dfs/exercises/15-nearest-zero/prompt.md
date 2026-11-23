# Distance to the nearest 0

`mat` is a grid of `0` and `1` with **at least one** `0`. Write `nearest_zero(mat)` that returns a grid where each cell holds the distance (number of steps up, down, left, right) to the **nearest `0`**.

```python
nearest_zero([[0, 0, 0], [0, 1, 0], [1, 1, 1]])    # -> [[0, 0, 0], [0, 1, 0], [1, 2, 1]]
nearest_zero([[0]])                                # -> [[0]]
```

**Think first:** asking every `1` to search for a `0` is slow. What if all the `0`s start spreading at the same time?

**Hint:** pattern *multi-source BFS*: queue all `0` cells with distance `0`; spread to neighbours not yet set; distance = parent distance + 1.
