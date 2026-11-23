# Pyramid

Write `pyramid(n)` that returns `n` rows. Row `i` has `n - i` leading spaces and `2 * i - 1` stars. No trailing spaces.

```python
pyramid(3)
# -> ['  *', ' ***', '*****']
```

**Think first:** fill a table for n = 3: row, spaces, stars.

**Hint:** `" " * (n - i) + "*" * (2 * i - 1)`.
