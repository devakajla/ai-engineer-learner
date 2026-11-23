# Rotting oranges

`grid` is a list of lists with `0` (empty), `1` (fresh orange), `2` (rotten orange). Every minute, each fresh orange that touches (up, down, left, right) a rotten one becomes rotten. Write `oranges_rotting(grid)` that returns the **minutes** until no fresh orange is left, or `-1` if some can never rot.

```python
oranges_rotting([[2, 1, 1], [1, 1, 0], [0, 1, 1]])    # -> 4
oranges_rotting([[2, 1, 1], [0, 1, 1], [1, 0, 1]])    # -> -1
```

**Think first:** all rotten oranges start spreading at the **same time**. Which search spreads in rounds?

**Hint:** pattern *multi-source BFS*: put **all** rotten cells in the queue first; each round of the queue is one minute; count fresh oranges and stop when it reaches 0.
