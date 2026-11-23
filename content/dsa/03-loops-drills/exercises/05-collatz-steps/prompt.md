# Collatz steps

Write `collatz_steps(n)` for `n >= 1`: while `n` is not 1, if it is even divide it by 2, otherwise do `3 * n + 1`. Return how many steps it took.

```python
collatz_steps(6)    # -> 8     (6 3 10 5 16 8 4 2 1)
collatz_steps(1)    # -> 0
```

**Think first:** how many steps for `n = 1`?

**Hint:** `while n != 1` with a step counter.
