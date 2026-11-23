# Closures with state

1. `make_counter(start=0, step=1)` returns a function; each call returns the next value: `start + step`, `start + 2*step`, ...
2. `make_rate_checker(limit)` returns a function `allow()` that returns `True` for the first `limit` calls and `False` afterwards — a tiny rate limiter. It must also expose a `reset()` function: return **both** as a tuple `(allow, reset)`.

Use closures and `nonlocal` (no classes, no globals).

```python
c = make_counter(10, 5)
c(), c()               # -> (15, 20)

allow, reset = make_rate_checker(2)
allow(), allow(), allow()   # -> (True, True, False)
reset(); allow()            # -> True
```
