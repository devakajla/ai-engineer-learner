# Invert a dict

Write `invert_dict(d)` that returns a new dict with keys and values swapped. All values are unique.

```python
invert_dict({"a": 1, "b": 2})   # -> {1: 'a', 2: 'b'}
invert_dict({})                 # -> {}
```

**Think first:** loop over pairs.

**Hint:** `for k, v in d.items()`.
