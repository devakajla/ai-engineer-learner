# All paths from source to target

`graph[i]` is the list of nodes you can go to **from** node `i` (a directed graph without cycles). Write `all_paths(graph)` that returns every path from node `0` to node `len(graph) - 1`, as lists of nodes. Return them in **sorted** order.

```python
all_paths([[1, 2], [3], [3], []])    # -> [[0, 1, 3], [0, 2, 3]]
all_paths([[]])                      # -> [[0]]
```

**Think first:** this is backtracking on a graph. What do you add to the path, and what do you undo?

**Hint:** pattern *DFS with path*: `go(node)`: append to `path`; if `node` is the target save a copy; else recurse into each neighbour; then pop. No `visited` set is needed because there are no cycles.
