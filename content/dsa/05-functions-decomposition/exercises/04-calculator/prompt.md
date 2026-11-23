# Small calculator

Write `calculate(a, op, b=0)` where `op` is `"+"`, `"-"`, `"*"`, `"/"` or `"neg"`. For `"neg"` return `-a` and ignore `b`. For `"/"` with `b == 0` return `None`. For any other `op` return `None`.

```python
calculate(6, "+", 2)    # -> 8
calculate(6, "/", 0)    # -> None
calculate(5, "neg")     # -> -5
```

**Think first:** which cases are special? Handle them first.

**Hint:** early returns, then one `if` per operator.
