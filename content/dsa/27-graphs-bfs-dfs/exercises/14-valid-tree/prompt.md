# Is the graph a tree?

Nodes are `0 .. n-1`, `edges` are undirected. The graph is a **tree** if it is connected and has no cycle. Write `valid_tree(n, edges)`.

```python
valid_tree(5, [[0, 1], [0, 2], [0, 3], [1, 4]])            # -> True
valid_tree(5, [[0, 1], [1, 2], [2, 3], [1, 3], [1, 4]])    # -> False   (cycle)
```

**Think first:** a tree with `n` nodes has exactly how many edges? What else must be true if you have that many edges?

**Hint:** pattern *edge count + one search*: if `len(edges) != n - 1` return `False`; then check that a search from node `0` reaches all `n` nodes.
