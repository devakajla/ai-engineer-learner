# Merge two sorted lists

Write `merge_sorted(a, b)` that returns one sorted list from two sorted lists. Do **not** call `sorted()` or `.sort()`: walk both lists with two indexes.

```python
merge_sorted([1, 3, 5], [2, 4, 6])   # -> [1, 2, 3, 4, 5, 6]
merge_sorted([], [1, 2])             # -> [1, 2]
merge_sorted([1, 1], [1])            # -> [1, 1, 1]
```

**Think first:** at each step, which two items do you compare? When one list runs out, what is left?

**Hint:** `i`, `j`, a `while i < len(a) and j < len(b)` loop, then add the rest.
