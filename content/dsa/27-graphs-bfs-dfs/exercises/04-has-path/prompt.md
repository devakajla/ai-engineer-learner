# Is there a path?

Nodes are `0 .. n-1` and `edges` are undirected. Write `has_path(n, edges, src, dst)` that returns `True` if you can walk from `src` to `dst`.

```python
has_path(4, [[0, 1], [1, 2]], 0, 2)    # -> True
has_path(4, [[0, 1], [2, 3]], 0, 3)    # -> False
```

**Think first:** explore everything reachable from `src`. Is `dst` in that set?

**Hint:** pattern *build graph + DFS/BFS*: adjacency list, then a `visited` set; return `dst in visited`.
