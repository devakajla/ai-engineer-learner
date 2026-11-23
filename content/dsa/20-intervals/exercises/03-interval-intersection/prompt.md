# Intersection of two interval lists

`a` and `b` are lists of **closed** intervals `[start, end]`. Inside each list the intervals do not overlap and are sorted. Write `interval_intersection(a, b)` that returns every overlap between an interval of `a` and an interval of `b`, sorted. If two intervals only touch at one point, the overlap is `[x, x]`.

```python
interval_intersection([[0, 2], [5, 10]], [[1, 5], [8, 12]])    # -> [[1, 2], [5, 5], [8, 10]]
interval_intersection([[1, 3]], [[4, 5]])                      # -> []
```

**Think first:** the overlap of two intervals is `[max(starts), min(ends)]`, if that is a real range. After that, which pointer can you move?

**Hint:** pattern *two pointers over two lists*: `lo = max(a[i][0], b[j][0])`, `hi = min(a[i][1], b[j][1])`; if `lo <= hi` save it. Advance the pointer of the interval that **ends first**.
