# Valid age

Write `is_valid_age(age)` that returns `True` only if `age` is an `int` (not a `bool`) between 0 and 120 **inclusive**.

```python
is_valid_age(25)     # -> True
is_valid_age(0)      # -> True
is_valid_age(121)    # -> False
is_valid_age(-1)     # -> False
is_valid_age("25")   # -> False
is_valid_age(True)   # -> False
```

Use a chained comparison. Think about the order of checks: what happens if you compare `"25" <= 120`?
