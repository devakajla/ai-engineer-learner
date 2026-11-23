# Build an adjacency list

A graph has nodes `0 .. n-1` and undirected `edges` like `[[0, 1], [1, 2]]` (each edge works in both directions, no repeats). Write `build_graph(n, edges)` that returns a dict: every node maps to the **sorted** list of its neighbours. Nodes without edges map to `[]`.

```python
build_graph(3, [[0, 1], [1, 2]])    # -> {0: [1], 1: [0, 2], 2: [1]}
build_graph(2, [])                  # -> {0: [], 1: []}
```

**Think first:** for one edge `[a, b]`, how many places do you write something?

**Hint:** pattern *adjacency list*: start with `{i: [] for i in range(n)}`; for each edge append `b` to `a`'s list and `a` to `b`'s list; sort at the end.
