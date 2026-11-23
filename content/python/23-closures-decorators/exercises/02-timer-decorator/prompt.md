# A timing decorator

Write a decorator `timed` that:

- calls the function with any arguments and returns its result
- records the duration in seconds by appending `(func.__name__, seconds)` to the module-level list `TIMINGS`
- records the timing **even if the function raises** (and re-raises the exception)
- preserves the function's name and docstring (`functools.wraps`)

```python
@timed
def add(a, b):
    """Add two numbers."""
    return a + b

add(2, b=3)        # -> 5
TIMINGS[-1][0]     # -> "add"
add.__name__       # -> "add"
```

Use `time.perf_counter()`.
