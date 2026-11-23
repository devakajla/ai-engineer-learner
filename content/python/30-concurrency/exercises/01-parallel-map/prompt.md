# Run jobs in parallel

Write two functions that use a `ThreadPoolExecutor`:

- `run_all(fn, items, max_workers=4)` runs `fn(item)` for every item and returns the results as a **list in the same order as `items`**.
- `try_all(fn, items, max_workers=4)` does the same, but a job that raises an error must not stop the others. Return a list in input order where each entry is `(True, result)` for success or `(False, error)` for a failure (`error` is the exception object).

For both: if `max_workers < 1`, raise `ValueError`.

```python
run_all(lambda x: x * 2, [1, 2, 3])      # -> [2, 4, 6]
try_all(lambda x: 10 // x, [5, 0, 2])    # -> [(True, 2), (False, ZeroDivisionError(...)), (True, 5)]
```

**Think first:** Which `executor` method gives results in input order? How do you read an error that happened inside a job?

**Hint:** `executor.map` for `run_all`. For `try_all`, use `executor.submit` and call `future.result()` inside a `try` / `except`.
