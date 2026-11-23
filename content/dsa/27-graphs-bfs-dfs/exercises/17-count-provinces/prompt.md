# Number of provinces

`connected[i][j] == 1` means city `i` and city `j` are directly connected (the matrix is symmetric and `connected[i][i] == 1`). A **province** is a group of cities connected directly or through other cities. Write `count_provinces(connected)`.

```python
count_provinces([[1, 1, 0], [1, 1, 0], [0, 0, 1]])    # -> 2
count_provinces([[1, 0], [0, 1]])                     # -> 2
```

**Think first:** this is "count components", but the graph comes as a matrix. What are the neighbours of city `i`?

**Hint:** pattern *components on an adjacency matrix*: neighbours of `i` are all `j` with `connected[i][j] == 1`; count the searches you start.
