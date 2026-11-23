# Minimum spanning tree cost

`edges` are undirected and weighted: `[u, v, w]`. Nodes are `0 .. n-1` and the graph is **connected**. A **spanning tree** connects all nodes with `n - 1` edges and no cycle. Write `mst_cost(n, edges)` that returns the smallest possible total weight.

```python
mst_cost(4, [[0, 1, 1], [1, 2, 2], [0, 2, 3], [2, 3, 1]])    # -> 4
mst_cost(1, [])                                              # -> 0
```

**Think first:** start with one node. Which edge leaving the tree should you add next to keep the cost small?

**Hint:** pattern *Prim with a heap*: push `(weight, node)` for edges from the tree; pop the cheapest; if the node is already in the tree skip it; else add its weight and push its edges.
