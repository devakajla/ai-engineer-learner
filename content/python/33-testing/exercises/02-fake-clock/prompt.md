# A rate limiter you can test without waiting

Write a class `RateLimiter` that allows at most `max_calls` calls in any window of `per_seconds` seconds.

- `RateLimiter(max_calls, per_seconds, clock)` – `clock` is a function with no arguments that returns the current time in seconds. It is given from outside, so tests can control time.
- `allow()` → `True` if a call is allowed now (and it is counted), otherwise `False` (and it is **not** counted).
- A call made at time `t` counts until time `t + per_seconds`. At exactly `t + per_seconds` it no longer counts.
- Raise `ValueError` if `max_calls < 1` or `per_seconds <= 0`.

```python
now = [0.0]
limiter = RateLimiter(2, 10, clock=lambda: now[0])
limiter.allow(), limiter.allow(), limiter.allow()   # -> True, True, False
now[0] = 10.0
limiter.allow()                                     # -> True   (the first two calls are now old)
```

**Think first:** What do you need to remember about earlier calls? How do you forget the old ones?

**Hint:** Keep a `collections.deque` of call times. At each `allow()`, remove times that are `<= now - per_seconds` from the left, then compare the length to `max_calls`.
