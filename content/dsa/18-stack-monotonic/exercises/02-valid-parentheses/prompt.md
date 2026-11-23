# Valid parentheses

`s` contains only `( ) [ ] { }`. Write `is_valid(s)` that returns `True` if every opening bracket is closed by the **same type** in the **correct order**.

```python
is_valid("()[]{}")    # -> True
is_valid("([)]")      # -> False
```

**Think first:** when a closing bracket arrives, which opening bracket must it match: the first one or the most recent one?

**Hint:** pattern *stack*: push openers; on a closer, the stack must not be empty and its top must be the matching opener (pop it). At the end the stack must be empty.
