# Common items

Write `common_items(a, b)` that returns a sorted list of the values that are in both lists, without repeats.

```python
common_items([1, 2, 2, 3], [2, 3, 4])   # -> [2, 3]
common_items([1], [2])                  # -> []
```

**Think first:** which set operation keeps items found in both?

**Hint:** `set(a) & set(b)` and `sorted(...)`.
