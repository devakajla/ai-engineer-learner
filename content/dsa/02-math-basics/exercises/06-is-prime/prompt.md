# Is it prime?

Write `is_prime(n)` that returns `True` if `n` is a prime number. A prime is greater than 1 and has no divisors except 1 and itself.

```python
is_prime(7)     # -> True
is_prime(12)    # -> False
is_prime(1)     # -> False
```

**Think first:** which small numbers (0, 1, 2) need special handling? What is the largest divisor you need to try?

**Hint:** try `i` from 2 while `i * i <= n`.
