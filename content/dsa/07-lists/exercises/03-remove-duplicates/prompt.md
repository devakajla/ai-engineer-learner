# Remove duplicates, keep order

Write `remove_duplicates(items)` that returns a new list with repeated values removed. Keep the first occurrence and the original order.

```python
remove_duplicates([3, 1, 3, 2, 1])   # -> [3, 1, 2]
remove_duplicates([])                # -> []
```

**Think first:** how do you know if you already saw a value?

**Hint:** build a result list; add only if `x not in result`.
