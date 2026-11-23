# A memoize decorator with expiry (TTL)

`lru_cache` never expires entries. Write a decorator factory `ttl_cache(seconds, clock=time.monotonic)`:

- caches results by the call's positional and keyword arguments (args are hashable)
- a cached value older than `seconds` is recomputed
- `clock` is injectable so tests control time
- the wrapper keeps the function's metadata and exposes `cache_clear()`

```python
now = [0.0]
@ttl_cache(seconds=10, clock=lambda: now[0])
def price(symbol): ...

price("AAPL"); price("AAPL")   # computed once
now[0] = 11
price("AAPL")                  # recomputed (expired)
```

Note: `f(1, b=2)` and `f(1, 2)` may be cached separately — that's fine.
