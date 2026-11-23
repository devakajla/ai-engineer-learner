# Only in one list

Write `only_in_one(a, b)` that returns a sorted list of values that are in exactly one of the two lists (not in both).

```python
only_in_one([1, 2, 3], [2, 3, 4])   # -> [1, 4]
only_in_one([1, 1], [1])            # -> []
```

**Think first:** this is the "symmetric difference".

**Hint:** `^` between two sets.
