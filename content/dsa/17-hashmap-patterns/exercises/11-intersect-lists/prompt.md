# Intersection of two lists (with repeats)

Write `intersect(a, b)` that returns the items that are in **both** lists. If a value appears 2 times in `a` and 3 times in `b`, it appears **2 times** in the result. Return the result **sorted ascending**.

```python
intersect([1, 2, 2, 1], [2, 2])           # -> [2, 2]
intersect([4, 9, 5], [9, 4, 9, 8, 4])     # -> [4, 9]
```

**Think first:** for one value, how many times can it be matched?

**Hint:** pattern *counter-dict (available)*: count `a`; walk `b` and use up a count when it is still above 0.
