# Safe int

Write `safe_int(text, default=0)` that converts `text` to an `int`. If the text is not a valid integer, return `default`.

```python
safe_int("42")            # -> 42
safe_int("abc")           # -> 0
safe_int("abc", -1)       # -> -1
safe_int("")              # -> 0
```
