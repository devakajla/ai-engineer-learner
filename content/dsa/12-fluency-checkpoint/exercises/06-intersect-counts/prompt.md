# Intersection with repeats

Write `intersect_counts(a, b)` that returns a sorted list of the values that appear in both lists. A value appears as many times as it appears in **both** lists (the smaller count).

```python
intersect_counts([1, 2, 2, 1], [2, 2])       # -> [2, 2]
intersect_counts([4, 9, 5], [9, 4, 9, 8, 4]) # -> [4, 9]
intersect_counts([1], [2])                   # -> []
```

**Think first:** count one list. Then walk the other list and "use up" counts.

**Hint:** counts dict of `a`; for each `x` in `b`, if `counts.get(x, 0) > 0`, add `x` and subtract 1. Finally `sorted`.
