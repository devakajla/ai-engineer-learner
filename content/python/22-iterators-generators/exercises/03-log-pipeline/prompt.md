# A lazy log pipeline

Each log line looks like `"2026-11-13T10:00:01 ERROR payment failed: timeout"` (timestamp, level, message).

Write three **generator** stages and one function:

- `parse(lines)` → yields dicts `{"ts": ..., "level": ..., "msg": ...}`; skip blank lines
- `filter_level(records, level)` → yields only records with that level
- `messages(records)` → yields just the `msg` strings
- `first_errors(lines, n)` → returns a **list** of the first `n` ERROR messages, built from the three stages and **stopping early** (don't consume more lines than needed)

```python
lines = ["t1 INFO started", "t2 ERROR db down", "", "t3 ERROR retry failed"]
first_errors(lines, 1)   # -> ["db down"]
```

The tests check laziness by passing a generator that fails if it's read too far.
