# Does it contain a digit?

Write `has_digit(n, d)` that returns `True` if the non-negative integer `n` contains the digit `d` (0-9).

```python
has_digit(1234, 3)   # -> True
has_digit(1234, 5)   # -> False
has_digit(0, 0)      # -> True
```

**Think first:** `0` has the digit 0, but a `while n > 0` loop would skip it.

**Hint:** peel digits and return `True` early; handle `n == 0` first.
