# Valid brackets (three kinds)

Write `is_valid(s)` that returns `True` if the string of `()[]{}` is balanced: every opener is closed by the same kind, in the right order.

```python
is_valid("([]{})")    # -> True
is_valid("(]")        # -> False
```

**Think first:** the most recent opener must be closed first. Which structure gives you "last in, first out"?

**Hint:** pattern *stack*: push openers; on a closer, the stack must be non-empty and its top must match; at the end the stack must be empty.
