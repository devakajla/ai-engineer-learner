# Count connected components

Nodes are `0 .. n-1`, `edges` are undirected. A **component** is a group of nodes that can reach each other. Write `count_components(n, edges)`.

```python
count_components(5, [[0, 1], [1, 2], [3, 4]])    # -> 2
count_components(3, [])                          # -> 3
```

**Think first:** start a search from a node you have not seen. How many times do you have to start a new search?

**Hint:** pattern *count the DFS starts*: for each node not visited: `count += 1` and explore all its component.
