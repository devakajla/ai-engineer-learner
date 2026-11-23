# Dijkstra: shortest distances

`edges` are directed and weighted: `[u, v, w]` means an arrow from `u` to `v` costing `w >= 0`. Nodes are `0 .. n-1`. Write `dijkstra(n, edges, src)` that returns a list with the shortest distance from `src` to every node. Use `float("inf")` for nodes that cannot be reached.

```python
dijkstra(3, [[0, 1, 4], [0, 2, 1], [2, 1, 2]], 0)    # -> [0, 3, 1]
dijkstra(2, [], 0)                                   # -> [0, inf]
```

**Think first:** BFS fails with different weights. Which node is safe to finalise next: the one with the smallest known distance. Which structure gives you that?

**Hint:** pattern *Dijkstra with a min-heap*: push `(distance, node)`; pop the smallest; skip it if the popped distance is bigger than `dist[node]`; relax each edge: `dist[v] = min(dist[v], d + w)` and push.
