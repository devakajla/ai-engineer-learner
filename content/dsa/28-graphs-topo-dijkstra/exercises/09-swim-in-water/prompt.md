# Swim in rising water

`grid` is `n x n` with **different** numbers `0 .. n*n - 1`: the height of each cell. At time `t` the water level is `t`, and you can stand on a cell if its height is `<= t`. You may swim 4-directionally between cells that are both under water. Start at the top-left at time 0. Write `swim_in_water(grid)` that returns the **least time** at which you can reach the bottom-right cell.

```python
swim_in_water([[0, 2], [1, 3]])    # -> 3
swim_in_water([[0]])               # -> 0
```

**Think first:** the cost of a path is its **highest** cell, not the sum. We want the path whose highest cell is the lowest.

**Hint:** pattern *Dijkstra with max*: heap of `(time_needed, r, c)`; the time to enter a neighbour is `max(current_time, grid[nr][nc])`; first time you pop the bottom-right, return its time.
