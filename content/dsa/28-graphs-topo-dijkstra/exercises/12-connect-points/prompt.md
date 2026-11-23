# Minimum cost to connect all points

`points` is a list of `[x, y]`. The cost to connect two points is their **Manhattan distance** `|x1 - x2| + |y1 - y2|`. Write `min_cost_connect(points)` that returns the smallest total cost to connect all points so that every point can reach every other.

```python
min_cost_connect([[0, 0], [2, 2], [3, 10], [5, 2], [7, 0]])    # -> 20
min_cost_connect([[0, 0]])                                     # -> 0
```

**Think first:** this is a minimum spanning tree where every pair of points is an edge. Do you need to build all edges first?

**Hint:** pattern *Prim without building edges*: keep `best[i]`, the cheapest cost to connect point `i` to the tree; each round take the unconnected point with the smallest `best` and update the others.
