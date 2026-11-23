# Bellman-Ford: negative weights

Edges `[u, v, w]` are directed and `w` may be **negative**. Nodes are `0 .. n-1`. Write `bellman_ford(n, edges, src)` that returns the list of shortest distances from `src` (`float("inf")` if unreachable), or `None` if a **negative cycle** can be reached from `src` (then distances are not defined).

```python
bellman_ford(3, [[0, 1, 4], [0, 2, 5], [1, 2, -3]], 0)    # -> [0, 4, 1]
bellman_ford(2, [[0, 1, 1], [1, 0, -2]], 0)               # -> None
```

**Think first:** a shortest path has at most `n - 1` edges. What if you can still improve a distance after `n - 1` rounds of relaxing every edge?

**Hint:** pattern *relax all edges n-1 times*: for each round, for each edge `if dist[u] + w < dist[v]` update. One more round: if anything still improves, return `None`. Skip edges whose `dist[u]` is infinite.
