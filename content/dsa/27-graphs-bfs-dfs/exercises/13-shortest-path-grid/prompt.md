# Shortest path in a grid maze

`grid` is a list of lists of `0` (free) and `1` (wall). You start at the top-left cell and want to reach the bottom-right cell, moving up, down, left or right through free cells. Write `shortest_path(grid)` that returns the **number of steps** of the shortest path, or `-1` if there is none. If the start or the end is a wall, return `-1`.

```python
shortest_path([[0, 0, 0], [1, 1, 0], [0, 0, 0]])    # -> 4
shortest_path([[0, 1], [1, 0]])                     # -> -1
```

**Think first:** every step costs the same. Which search finds the fewest steps first?

**Hint:** pattern *BFS on a grid*: queue of `(row, col, steps)` (or round by round); mark a cell visited when you push it.
