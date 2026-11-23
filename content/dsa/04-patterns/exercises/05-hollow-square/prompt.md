# Hollow square

Write `hollow_square(n)` that returns `n` rows of width `n`. The border is `*`; the inside is spaces. For `n = 1` return `['*']`.

```python
hollow_square(4)
# -> ['****', '*  *', '*  *', '****']
```

**Think first:** which rows are full? What do the other rows look like?

**Hint:** first and last row are all stars. Middle rows: `"*" + " " * (n - 2) + "*"`.
