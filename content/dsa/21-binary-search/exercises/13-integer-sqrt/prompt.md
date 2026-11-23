# Integer square root

Write `int_sqrt(x)` that returns the square root of `x` **rounded down** (`x >= 0`). Do not use `**0.5`, `sqrt` or `isqrt`.

```python
int_sqrt(8)     # -> 2
int_sqrt(16)    # -> 4
```

**Think first:** the answer is a number between `0` and `x`. For a guess `m`, how do you know if it is too big?

**Hint:** pattern *binary search on the answer*: find the largest `m` with `m * m <= x`. If `m * m <= x` save `m` and go right, else go left.
