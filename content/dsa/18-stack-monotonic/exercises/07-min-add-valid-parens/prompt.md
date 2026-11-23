# Minimum additions to make parentheses valid

`s` contains only `(` and `)`. Write `min_add_to_make_valid(s)` that returns the smallest number of parentheses you must **insert** to make `s` valid.

```python
min_add_to_make_valid("())")     # -> 1
min_add_to_make_valid("(((")     # -> 3
```

**Think first:** do you need a full stack, or is a single counter of open brackets enough here?

**Hint:** pattern *counter instead of stack*: `open_count` goes up on `(`; on `)` it goes down if positive, otherwise you need one extra `(` (`added += 1`). Answer `added + open_count`.
