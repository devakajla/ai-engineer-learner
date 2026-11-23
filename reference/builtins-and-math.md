# Built-ins and math

| Name | Does | Returns |
| --- | --- | --- |
| `len(x)` | number of items | int |
| `sum(nums)` | total | number |
| `min(...)` / `max(...)` | smallest / largest | item |
| `abs(n)` | distance from zero | number |
| `round(x, d)` | round to `d` decimals | number |
| `divmod(a, b)` | `(a // b, a % b)` | tuple |
| `range(a, b, s)` | numbers from `a` up to (not including) `b` | range |
| `a // b`, `a % b`, `a ** b` | floor divide, remainder, power | number |

## `//` and `%`

**Theory:** `//` divides and rounds **down**. `%` is the remainder. Always `a == (a // b) * b + a % b`.
```python
print(17 // 5, 17 % 5)   # -> 3 2
print(-7 // 2, -7 % 2)   # -> -4 1
```
**Gotcha:** `/` always gives a float. For whole numbers use `//`. Lesson: `dsa/02-math-basics`.

## `divmod(a, b)`

**Theory:** quotient and remainder together.
```python
q, r = divmod(17, 5)
print(q, r)   # -> 3 2
```

## `abs`, `round`, `**`

```python
print(abs(-8))             # -> 8
print(round(3.14159, 2))   # -> 3.14
print(round(2.5), round(3.5))   # -> 2 4
print(2 ** 10)             # -> 1024
```
**Gotcha:** `round` rounds half to even (2.5 -> 2).

## `range(start, stop, step)`

**Theory:** a lazy sequence of numbers; `stop` is **not** included. Use `list(range(...))` to see it.
```python
print(list(range(3)))          # -> [0, 1, 2]
print(list(range(2, 8, 2)))    # -> [2, 4, 6]
print(list(range(5, 0, -1)))   # -> [5, 4, 3, 2, 1]
```
**Gotcha:** `range(1, n)` stops at `n - 1`. Use `range(1, n + 1)` to include `n`.

## `sum`, `min`, `max`, `len`

```python
nums = [4, 1, 7]
print(sum(nums), min(nums), max(nums), len(nums))   # -> 12 1 7 3
```
**Gotcha:** `min([])` and `max([])` raise `ValueError`. Check for an empty list first.

## Digit tricks

**Theory:** last digit is `n % 10`; remove it with `n // 10`.
```python
n = 1234
print(n % 10, n // 10)   # -> 4 123
```
Peel-digits loop: `while n > 0: use(n % 10); n //= 10`. Lesson: `dsa/02-math-basics`.

## Divisibility and divisors

`b % a == 0` means `a` divides `b`. Check divisors only while `i * i <= n`, because they come in pairs.
