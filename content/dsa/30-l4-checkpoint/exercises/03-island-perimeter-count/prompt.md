# Count islands bigger than K

`grid` is a list of strings of `"1"` (land) and `"0"` (water). Write `big_islands(grid, k)` that returns how many islands have **more than `k` cells**. Connections are up, down, left, right.

```python
big_islands(["110", "110", "001"], 1)    # -> 1
big_islands(["101", "010", "101"], 0)    # -> 5
```

**Think first:** you need each island's size, not only the count.

**Hint:** pattern *grid flood with counter*: search from each unvisited land cell, count its cells, compare with `k`.
