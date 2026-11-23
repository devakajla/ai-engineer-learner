# Compute each value only once, even with many threads

Write a class `OnceCache`:

- `get_or_compute(key, compute)` – if `key` is already stored, return it. Otherwise call `compute(key)`, store the result, and return it.
- It must be **thread-safe**: if many threads ask for the same key at the same time, `compute` runs **only once** for that key, and all threads get the same value.
- `__len__` returns the number of stored keys.
- If `compute` raises an error, nothing is stored, and the error goes to the caller. The next call tries again.

```python
cache = OnceCache()
cache.get_or_compute("a", lambda k: k.upper())     # -> "A"
cache.get_or_compute("a", lambda k: "other")       # -> "A"   (already stored)
len(cache)                                         # -> 1
```

**Think first:** Two threads both see "not stored yet" at the same moment. What goes wrong? What must the lock cover: only the check, only the work, or both?

**Hint:** One `threading.Lock`. Do the check, the `compute` call and the store inside the same `with self._lock:` block.
