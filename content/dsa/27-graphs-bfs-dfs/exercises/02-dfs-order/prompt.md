# DFS visit order

`graph` is a dict `{node: [neighbours]}` (undirected, connected parts may exist). Write `dfs_order(graph, start)` that returns the nodes reachable from `start` in **depth-first** order. Visit neighbours in the order they are listed. Never visit a node twice.

```python
g = {0: [1, 2], 1: [0, 3], 2: [0], 3: [1]}
dfs_order(g, 0)    # -> [0, 1, 3, 2]
```

**Think first:** a graph can have cycles. What stops you from walking in circles?

**Hint:** pattern *DFS with a visited set*: `visit(node)`: add to `visited` and to the result; for each neighbour not visited, `visit(neighbour)`.
