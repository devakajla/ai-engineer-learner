# Backoff delays

Write `backoff_delays(tries, base=1, cap=30)`. It returns the list of seconds to wait before each retry, doubling every time.

Rules:
- The wait for attempt number `i` (starting at 0) is `base * 2 ** i`.
- No wait may be larger than `cap`. Use `min`.
- Return a list with `tries` items. If `tries` is `0`, return `[]`.

```python
backoff_delays(4)                 # -> [1, 2, 4, 8]
backoff_delays(6, base=1, cap=10) # -> [1, 2, 4, 8, 10, 10]
backoff_delays(3, base=0.5)       # -> [0.5, 1.0, 2.0]
backoff_delays(0)                 # -> []
```
