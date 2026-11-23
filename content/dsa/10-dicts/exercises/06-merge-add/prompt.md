# Merge two count dicts

Write `merge_add(a, b)` that returns a new dict with all keys from both. If a key is in both, add the values.

```python
merge_add({"a": 1, "b": 2}, {"b": 3, "c": 4})
# -> {'a': 1, 'b': 5, 'c': 4}
```

**Think first:** start from a copy of `a`; then handle each key of `b`.

**Hint:** `result.get(k, 0) + v`.
