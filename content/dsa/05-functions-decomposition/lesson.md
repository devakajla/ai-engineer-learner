---
title: "Functions and decomposition"
summary: "Break a problem into small functions: helpers, default arguments, early returns and returning several values."
plan_ids: []
---

Big problems become easy when you split them into small functions. Each function does one thing and has a clear name.

## Helper functions

Write a small function, then use it inside another.

```python
def is_even(n):
    return n % 2 == 0

def count_even(numbers):
    count = 0
    for n in numbers:
        if is_even(n):
            count += 1
    return count

print(count_even([1, 2, 4]))   # -> 2
```

> If you can name a piece of logic ("is this a leap year?"), make it a function. It is easier to test alone.

## Return several values

Return a tuple and unpack it:

```python
def min_max(a, b):
    if a < b:
        return a, b
    return b, a

low, high = min_max(9, 3)
print(low, high)   # -> 3 9
```

## Default and keyword arguments

```python
def power(base, exp=2):
    return base ** exp

print(power(5))            # -> 25
print(power(2, 10))        # -> 1024
print(power(exp=3, base=2))   # -> 8
```

## Early return

Handle the special cases first and return. The rest of the function stays simple.

```python
def safe_divide(a, b):
    if b == 0:
        return None
    return a / b

print(safe_divide(6, 3))   # -> 2.0
print(safe_divide(1, 0))   # -> None
```

## Functions call functions

```python
def is_prime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True

def primes_up_to(n):
    result = []
    for k in range(2, n + 1):
        if is_prime(k):
            result.append(k)
    return result

print(primes_up_to(10))   # -> [2, 3, 5, 7]
```

Each function can be tested alone. If `primes_up_to` is wrong, check `is_prime` first.

## Constants and lookup lists

For fixed data (like days per month) keep a list or dict near the function instead of many `if`s:

```python
DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
print(DAYS[1])   # -> 28
```

## Common mistakes

- One huge function that does everything.
- Changing the meaning of a helper while using it elsewhere.
- Forgetting to return in a helper.
- Using a mutable default argument like `def f(x, items=[])` (a classic trap; you will see why later).

## Summary

- Split by name: if you can name a step, make it a function.
- Return tuples for several results, unpack on the other side.
- Defaults make common calls short.
- Early return for special cases.
- Test helpers first when a bigger function fails.
