# Count multiples

Write `count_multiples(n, k)` that returns how many numbers from 1 to `n` (inclusive) are divisible by `k`. `k` is at least 1.

```python
count_multiples(10, 3)   # -> 3     (3, 6, 9)
count_multiples(5, 7)    # -> 0
```

**Think first:** is `n` itself included?

**Hint:** counter pattern with `%`.
