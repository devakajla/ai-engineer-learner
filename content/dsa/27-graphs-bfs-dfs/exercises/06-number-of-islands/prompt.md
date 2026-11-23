# Number of islands

`grid` is a list of strings made of `"1"` (land) and `"0"` (water). An **island** is a group of land cells connected up, down, left or right. Write `num_islands(grid)`.

```python
num_islands(["11000", "11000", "00100", "00011"])    # -> 3
num_islands(["000"])                                 # -> 0
```

**Think first:** this is "count components" on a grid. What are the neighbours of a cell? How do you avoid counting a cell twice?

**Hint:** pattern *grid DFS flood*: for each unvisited land cell: `count += 1`, then visit all connected land (use a `visited` set of `(row, col)` or a stack).
