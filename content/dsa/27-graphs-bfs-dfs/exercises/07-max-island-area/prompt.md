# Biggest island

Same grid as before (`"1"` land, `"0"` water). Write `max_island_area(grid)` that returns the number of cells of the **biggest** island (`0` if no land).

```python
max_island_area(["11000", "11000", "00100", "00011"])    # -> 4
max_island_area(["00"])                                  # -> 0
```

**Think first:** while you explore one island, what do you count?

**Hint:** pattern *flood fill with a counter*: start a search on each unvisited land cell; its size is the number of cells you visit; keep the maximum.
