# A counter that is safe for many threads

Write a class `SafeCounter`:

- `SafeCounter(start=0)` starts at `start`.
- `increment(n=1)` adds `n` to the value. It must be **safe when many threads call it at the same time**: no update may be lost.
- `value` is a property that gives the current number.
- `reset()` sets the value back to `0`.

Use a `threading.Lock` and a `with` block.

```python
c = SafeCounter()
c.increment(); c.increment(5)
c.value          # -> 6
# 8 threads each calling increment() 5000 times -> c.value == 40000
```

**Think first:** `self._value += n` is not one step. What are the steps, and why can two threads mix them up?

**Hint:** Make one `threading.Lock()` in `__init__`, and wrap the change in `with self._lock:`.
