# Two ways to build a timer

1. A class `Timer` usable as `with Timer() as t:` — after the block, `t.elapsed` holds the seconds (float). It must **not** suppress exceptions, and `elapsed` must be set even if the block raised.
2. A function `timer(results, label)` decorated with `@contextmanager` that appends `(label, seconds)` to the `results` list when the block ends — also on exceptions.

```python
with Timer() as t:
    time.sleep(0.01)
t.elapsed >= 0.01        # -> True

results = []
with timer(results, "query"):
    ...
results                  # -> [("query", 0.0001...)]
```
