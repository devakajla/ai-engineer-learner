# Path with maximum probability

Nodes are `0 .. n-1`. Each undirected edge `[a, b]` has a success probability `probs[i]` (between 0 and 1). The probability of a path is the **product** of its edge probabilities. Write `max_probability(n, edges, probs, start, end)` that returns the biggest probability of a path from `start` to `end`, or `0.0` if there is no path.

```python
max_probability(3, [[0, 1], [1, 2], [0, 2]], [0.5, 0.5, 0.2], 0, 2)    # -> 0.25
max_probability(3, [[0, 1]], [0.5], 0, 2)                              # -> 0.0
```

**Think first:** Dijkstra picks the smallest cost. How do you make the **biggest** probability come out first?

**Hint:** pattern *Dijkstra for a max product*: push `(-probability, node)`; pop the best; for each edge the new probability is `p * edge_prob`; keep only improvements.
