# Valid brackets

Write `valid_brackets(s)` that returns `True` if every `(`, `[`, `{` is closed by the matching bracket in the right order. Other characters do not appear.

```python
valid_brackets("([]{})")   # -> True
valid_brackets("(]")       # -> False
valid_brackets("((")       # -> False
```

**Think first:** the most recent opening bracket must be closed first. A list can hold the "open" brackets: add to the end, remove from the end.

**Hint:** `stack.append(ch)` on open; on close, `stack.pop()` and compare using a dict like `{")": "(", ...}`. Watch for popping an empty list.
