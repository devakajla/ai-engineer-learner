---
title: Numbers & casting
summary: Whole numbers and decimals, the math operators, rounding, why decimals can be slightly off, and how to change one type into another.
plan_ids: []
---

Numbers look easy, but they hide a few surprises that catch almost everyone: `0.1 + 0.2`, `round(2.5)` and money. This lesson shows you the surprises so they do not catch you.

## Two kinds of numbers

- `int` is a whole number: `5`, `-12`, `0`.
- `float` is a number with a decimal point: `3.14`, `-0.5`, `2.0`.

A Python `int` can be as big as you like. It never "overflows". Underscores in a number are only there to help you read it:

```python
2 ** 100          # -> 1267650600228229401496703205376
big = 1_000_000   # the same as 1000000
```

## Math operators

| Operator | Meaning | Example | Result |
|---|---|---|---|
| `+` `-` `*` | add, subtract, multiply | `2 + 3` | `5` |
| `/` | division (always gives a float) | `7 / 2` | `3.5` |
| `//` | floor division (the whole-number part) | `7 // 2` | `3` |
| `%` | remainder (what is left over) | `7 % 2` | `1` |
| `**` | power | `2 ** 10` | `1024` |

`/` always gives a float, even when the answer is a whole number:

```python
7 / 2     # -> 3.5
4 / 2     # -> 2.0
```

`//` and `%` work as a pair. `7 // 2` asks "how many full 2s fit in 7?" (3). `7 % 2` asks "what is left?" (1).

```python
17 // 5    # -> 3
17 % 5     # -> 2    (3 * 5 + 2 = 17)
10 % 2     # -> 0    a number is even if its remainder by 2 is 0
```

`divmod(a, b)` gives both answers at once, as a pair `(a // b, a % b)`. A pair like this is called a **tuple** (you will learn tuples in lesson 9).

Here is a step-by-step example. How many full weeks and extra days are in 17 days?

1. Full weeks: `17 // 7` is `2`.
2. Days left: `17 % 7` is `3`.
3. `divmod(17, 7)` gives both at once.

```python
divmod(17, 7)    # -> (2, 3)   2 weeks and 3 days
```

## Rounding

`round(number, digits)` rounds a number to the digits you ask for.

```python
round(2.567, 2)   # -> 2.57
round(3.14159, 1) # -> 3.1
round(7.6)        # -> 8
```

Now the surprise. When a number is exactly half way, `round()` goes to the nearest **even** number:

```python
round(2.5)   # -> 2   (not 3!)
round(3.5)   # -> 4
round(4.5)   # -> 4
```

This is called **banker's rounding**. It is fair over many numbers, but it surprises people.

`int()` is different. It just cuts off the decimal part. It does **not** round:

```python
int(3.99)    # -> 3
int(-3.99)   # -> -3
```

## Changing types (casting)

Changing a value from one type to another is called **casting**. You do it by calling the type like a function:

```python
int("42")       # -> 42       text to whole number
int("  42  ")   # -> 42       spaces around the text are ignored
float("1.5")    # -> 1.5      text to decimal number
float(3)        # -> 3.0
str(3.0)        # -> '3.0'    number to text
int(3.99)       # -> 3        cuts the decimal part
```

`int()` only understands text that looks like a whole number. Other text gives a `ValueError`:

```python
int("3.5")          # ValueError: invalid literal for int() with base 10: '3.5'
int(float("3.5"))   # -> 3     first to float, then to int
```

Python never turns text into a number (or the other way round) by itself. You must cast. But Python is happy to mix `int` and `float` in math:

```python
1 + 2.0     # -> 3.0
"5" + 5     # TypeError. Cast first: int("5") + 5 -> 10
```

`bool()` turns a value into `True` or `False`. Zero and empty things become `False`. You will see more of this in lesson 5.

```python
bool(0)      # -> False
bool("")     # -> False
bool(7)      # -> True
```

## Decimals are not exact

Computers keep decimals in binary, and many decimals (like `0.1`) cannot be stored exactly. So you get tiny errors:

```python
0.1 + 0.2             # -> 0.30000000000000004
0.1 + 0.2 == 0.3      # -> False
```

This is not a Python bug. It happens in almost every language. Two ways to deal with it:

1. To compare floats, check if they are *close*, using `math.isclose`. (`import` lets you use extra tools. You will learn it in lesson 14.)
2. For **money**, never use floats. Keep money as whole numbers of the smallest unit, like paise or cents. Rs 19.99 is `1999` paise.

```python
import math
math.isclose(0.1 + 0.2, 0.3)   # -> True
```

## The `int(float * 100)` trap

Suppose a price comes as the text `"19.99"` and you want paise. The obvious way is wrong:

```python
float("19.99") * 100          # -> 1998.9999999999998
int(float("19.99") * 100)     # -> 1998   wrong by one paisa!
round(float("19.99") * 100)   # -> 1999   correct
```

`int()` cuts off the decimal part, so the tiny error became a real mistake. `round()` fixes it.

## A little deeper (optional)

**Floor division with negative numbers.** `//` rounds **down** (towards smaller numbers), not towards zero.

```python
7 // 2     # -> 3
-7 // 2    # -> -4    because -3.5 rounded down is -4
-7 % 2     # -> 1
```

This is different from C, Java and JavaScript. It is a popular interview question.

**Other ways to round.**

```python
import math
math.floor(-2.5)   # -> -3   down
math.ceil(-2.5)    # -> -2   up
int(-2.5)          # -> -2   cuts the decimal part (towards zero)
```

**Exact decimals.** The `Decimal` type stores decimals exactly. It is slower, but good for money:

```python
from decimal import Decimal
Decimal("0.1") + Decimal("0.2")   # -> Decimal('0.3')
```

**Other number bases.** `int("ff", 16)` reads the text as a base-16 number and gives `255`.

## Common mistakes

- Comparing floats with `==`. Use `math.isclose`, or work with whole numbers.
- Expecting `round(2.5)` to be `3`. It is `2`.
- Expecting `-7 // 2` to be `-3`. It is `-4`.
- Using `int()` when you meant to round.
- Storing money as floats.

## Summary

- `int` is a whole number (any size). `float` is a decimal number and is not always exact.
- `/` gives a float. `//` gives the whole-number part. `%` gives the remainder. `divmod(a, b)` gives both.
- `round()` sends exact halves to the even number. `int()` cuts the decimal part.
- Change types on purpose with `int()`, `float()`, `str()` and `bool()`. `int("3.5")` is a `ValueError`.
- For money, use whole numbers of the smallest unit (or `Decimal`), and `round()` after converting.
