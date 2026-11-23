# Cheapest path in a cost grid

`grid` is a rectangle of positive numbers (the cost of entering each cell). You start at the top-left, go to the bottom-right, moving **up, down, left or right**. The cost of a path is the sum of the cells on it (including start and end). Write `cheapest_path(grid)`.

```python
cheapest_path([[1, 3, 1], [1, 5, 1], [4, 2, 1]])    # -> 7
cheapest_path([[5]])                                # -> 5
```

**Think first:** moves in all four directions: is plain DP over rows and columns enough? What handles weights?

**Hint:** pattern *Dijkstra on a grid*: heap of `(cost, r, c)`; first time you pop the bottom-right cell, that cost is the answer.
