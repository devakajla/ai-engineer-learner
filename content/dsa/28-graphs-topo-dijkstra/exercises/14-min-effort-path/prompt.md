# Path with minimum effort

`heights` is a grid of numbers. Move up, down, left or right from the top-left to the bottom-right cell. The **effort** of a path is the biggest absolute height difference between two **neighbouring cells on the path**. Write `min_effort(heights)` that returns the smallest possible effort.

```python
min_effort([[1, 2, 2], [3, 8, 2], [5, 3, 5]])    # -> 2
min_effort([[1, 10], [10, 1]])                   # -> 9
```

**Think first:** like swimming in water, the cost is a **maximum**, not a sum. What do you push into the heap?

**Hint:** pattern *Dijkstra with max*: heap of `(effort, r, c)`; effort to a neighbour is `max(effort, abs(h[nr][nc] - h[r][c]))`; the first time you pop the last cell, that effort is the answer.
