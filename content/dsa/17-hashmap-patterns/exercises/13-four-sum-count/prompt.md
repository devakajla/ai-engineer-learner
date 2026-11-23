# 4Sum count

Four lists `a`, `b`, `c`, `d` have the same length `n`. Write `four_sum_count(a, b, c, d)` that counts the tuples `(i, j, k, l)` with `a[i] + b[j] + c[k] + d[l] == 0`. Aim for O(n²), not O(n⁴).

```python
four_sum_count([1, 2], [-2, -1], [-1, 2], [0, 2])    # -> 2
four_sum_count([0], [0], [0], [0])                   # -> 1
```

**Think first:** split the four lists into two halves. If you know every sum of the first half, what do you look up for each sum of the second half?

**Hint:** pattern *pair sums in a dict*: count all `a[i] + b[j]`, then for every `c[k] + d[l]` add `counts.get(-(c + d), 0)`.
