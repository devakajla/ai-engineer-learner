# Count the shortest paths

`edges` are undirected `[u, v, w]` with `w > 0`. Nodes are `0 .. n-1`. Write `count_shortest_paths(n, edges)` that returns **how many different paths** from node `0` to node `n - 1` have the smallest possible total weight. Return `0` if there is no path.

```python
count_shortest_paths(4, [[0, 1, 1], [0, 2, 1], [1, 3, 1], [2, 3, 1]])    # -> 2
count_shortest_paths(3, [[0, 1, 1]])                                     # -> 0
```

**Think first:** while running Dijkstra, what do you do when you find a path to a node that is **equal** to the best distance so far?

**Hint:** pattern *Dijkstra + counter*: keep `ways[node]`; on a **shorter** distance set `ways[nb] = ways[node]`; on an **equal** distance add `ways[node]` to `ways[nb]`.
