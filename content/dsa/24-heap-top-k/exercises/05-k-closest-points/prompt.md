# K closest points to the origin

`points` is a list of `[x, y]`. Write `k_closest(points, k)` that returns the `k` points closest to `(0, 0)` (straight-line distance). Order: nearest first; for equal distance, smaller `x` first, then smaller `y`. Compare **squared** distances (`x*x + y*y`), no square roots.

```python
k_closest([[1, 3], [-2, 2]], 1)              # -> [[-2, 2]]
k_closest([[3, 3], [5, -1], [-2, 4]], 2)     # -> [[3, 3], [-2, 4]]
```

**Think first:** what number do you put first in a tuple so the heap orders by distance?

**Hint:** pattern *heap of pairs*: push `(x*x + y*y, x, y)`; pop `k` times.
