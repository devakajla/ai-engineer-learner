# Cycle in a directed graph

Nodes are `0 .. n-1`; each edge `[a, b]` goes **from a to b**. Write `has_cycle_directed(n, edges)` that returns `True` if you can start at some node and come back to it by following arrows.

```python
has_cycle_directed(3, [[0, 1], [1, 2], [2, 0]])    # -> True
has_cycle_directed(3, [[0, 1], [0, 2], [1, 2]])    # -> False
```

**Think first:** in a directed graph a visited node is not always a cycle (two paths can meet). What is special about nodes on the **current path**?

**Hint:** pattern *DFS with three states*: `0` new, `1` on the current path, `2` finished. Reaching a node with state `1` means a cycle. Set `2` when you leave a node.
