# Is it a real number?

Write `is_number(value)` that returns `True` if `value` is an `int` or a `float`, and `False` otherwise.

**Twist:** booleans must return `False` — `True` is not a number for our purposes.

```python
is_number(3)       # -> True
is_number(2.5)     # -> True
is_number("3")     # -> False
is_number(True)    # -> False
is_number(None)    # -> False
```

Hint: re-read why `isinstance(True, int)` is `True`. You can combine checks with `and` and `not` (covered fully in lesson 5): `A and not B`.
