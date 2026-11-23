---
title: "Math basics"
summary: "The math operators you need for digit and number problems: // % ** abs round divmod."
plan_ids: []
---

Many beginner problems are really small math problems: digits of a number, divisors, primes. A few operators solve most of them.

## `//` and `%` (the pair you will use most)

`//` is floor division (divide and drop the fraction). `%` is the remainder.

```python
print(17 // 5)    # -> 3
print(17 % 5)     # -> 2
print(-7 // 2)    # -> -4   (rounds down, not toward zero)
print(-7 % 2)     # -> 1
```

Rule: `a == (a // b) * b + a % b`.

## `divmod`

Get both at once:

```python
q, r = divmod(17, 5)
print(q, r)   # -> 3 2
```

## `**`, `abs`, `round`

```python
print(2 ** 10)        # -> 1024
print(abs(-8))        # -> 8
print(round(3.14159, 2))   # -> 3.14
print(round(2.5))     # -> 2   (rounds half to even)
```

## Digits of a number

The last digit is `n % 10`. Remove the last digit with `n // 10`.

```python
n = 1234
print(n % 10)     # -> 4
print(n // 10)    # -> 123
```

Loop until the number is 0:

```python
n = 1234
total = 0
while n > 0:
    total += n % 10
    n //= 10
print(total)   # -> 10
```

> Pattern: **peel digits**. Take the last digit, use it, drop it, repeat.

## Divisibility

`a` divides `b` evenly when `b % a == 0`.

```python
print(12 % 3 == 0)   # -> True
print(12 % 5 == 0)   # -> False
```

## Loop up to a square root

To check divisors of `n` you only need to try numbers up to `sqrt(n)`. Use `i * i <= n`:

```python
n = 36
i = 1
while i * i <= n:
    if n % i == 0:
        print(i, n // i)
    i += 1
# -> 1 36
# -> 2 18
# -> 3 12
# -> 4 9
# -> 6 6
```

## Common mistakes

- Using `/` (gives a float) when you want `//`.
- Forgetting `n //= 10` inside the loop: infinite loop.
- Working with negative numbers without `abs`.
- Checking `n % 2 == 1` for odd numbers: fails for negatives in other languages; use `n % 2 != 0`.

## Summary

- `//` drops the fraction, `%` gives the remainder, `divmod` gives both.
- Last digit: `n % 10`. Remove it: `n // 10`.
- Divisible: `b % a == 0`.
- Divisors come in pairs, so loop only while `i * i <= n`.
- Reference: `reference/builtins-and-math.md`.
