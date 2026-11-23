# Shortest path length (no weights)

Nodes are `0 .. n-1`, `edges` are undirected, every edge costs 1 step. Write `shortest_path_len(n, edges, src, dst)` that returns the fewest edges on a path from `src` to `dst`, or `-1` if there is none.

```python
shortest_path_len(5, [[0, 1], [1, 2], [0, 3], [3, 2], [2, 4]], 0, 4)    # -> 3
shortest_path_len(3, [[0, 1]], 0, 2)                                    # -> -1
```

**Think first:** which search reaches the nearest nodes first?

**Hint:** pattern *BFS with distances*: `dist = {src: 0}`; when you push a neighbour set `dist[nb] = dist[node] + 1`.
