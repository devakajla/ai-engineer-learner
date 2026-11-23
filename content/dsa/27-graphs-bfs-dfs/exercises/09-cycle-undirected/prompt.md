# Cycle in an undirected graph

Nodes are `0 .. n-1`; `edges` are undirected, with no repeated edges and no self loops. Write `has_cycle_undirected(n, edges)` that returns `True` if the graph has a cycle.

```python
has_cycle_undirected(3, [[0, 1], [1, 2], [2, 0]])    # -> True
has_cycle_undirected(4, [[0, 1], [1, 2]])            # -> False
```

**Think first:** in a DFS, you see an already visited node. When is that **not** a cycle?

**Hint:** pattern *DFS with parent*: `visit(node, parent)`: for each neighbour except `parent`: if already visited, a cycle exists; else recurse. Try every unvisited node as a start.
