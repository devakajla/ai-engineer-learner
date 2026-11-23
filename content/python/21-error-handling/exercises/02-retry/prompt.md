# Retry with exponential backoff

Write `retry(fn, attempts=3, base_delay=0.5, retry_on=(ConnectionError, TimeoutError), sleep=time.sleep)`:

- calls `fn()` and returns its result
- if `fn` raises one of `retry_on`, wait and try again, up to `attempts` calls in total
- waits are `base_delay * 2 ** (n - 1)` for the n-th retry: `0.5, 1.0, 2.0, ...` (no jitter here, so it's testable)
- after the last attempt fails, **re-raise** that exception
- any other exception is raised **immediately** (no retry)
- `sleep` is injectable so tests don't actually wait

```python
calls = iter([ConnectionError(), ConnectionError(), "ok"])
def flaky():
    item = next(calls)
    if isinstance(item, Exception):
        raise item
    return item

retry(flaky, sleep=delays.append)   # -> "ok", delays == [0.5, 1.0]
```
