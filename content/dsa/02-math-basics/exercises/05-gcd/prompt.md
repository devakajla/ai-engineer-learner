# Greatest common divisor

Write `gcd(a, b)` that returns the greatest common divisor of two positive integers. Do not use `math.gcd`.

```python
gcd(12, 18)   # -> 6
gcd(7, 13)    # -> 1
gcd(10, 10)   # -> 10
```

**Think first:** start from the smaller number and count down. The first number that divides both is the answer.

**Hint:** `for i in range(min(a, b), 0, -1)`, check `a % i == 0 and b % i == 0`.
