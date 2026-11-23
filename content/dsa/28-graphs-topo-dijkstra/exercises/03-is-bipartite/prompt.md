# Is the graph bipartite?

A graph is **bipartite** if you can colour every node with one of two colours so that **no edge joins two nodes of the same colour**. `graph[i]` is the list of neighbours of node `i` (undirected; the lists agree with each other). Write `is_bipartite(graph)`. The graph may be disconnected.

```python
is_bipartite([[1, 3], [0, 2], [1, 3], [0, 2]])    # -> True
is_bipartite([[1, 2, 3], [0, 2], [0, 1, 3], [0, 2]])    # -> False
```

**Think first:** colour one node. What must be the colour of all its neighbours? What if a neighbour already has the same colour?

**Hint:** pattern *graph colouring with BFS/DFS*: dict `colour`; for every uncoloured node colour it `0` and spread; neighbours get `1 - colour`; a neighbour with the same colour means `False`.
