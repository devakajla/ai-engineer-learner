# Primes up to n

Write `primes_up_to(n)` that returns a list of all primes from 2 to `n` (inclusive). Use a helper `is_prime` in the same file.

```python
primes_up_to(10)    # -> [2, 3, 5, 7]
primes_up_to(1)     # -> []
primes_up_to(2)     # -> [2]
```

**Think first:** you wrote `is_prime` before. What is the outer loop?

**Hint:** build-list pattern calling `is_prime(k)`.
