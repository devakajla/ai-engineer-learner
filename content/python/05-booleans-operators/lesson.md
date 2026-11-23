---
title: Booleans & operators
summary: True and False, which values count as true, comparing, and how and / or / not decide.
plan_ids: []
---

A program often needs to answer yes or no: "Is the user old enough?", "Is the list empty?". In Python the answer is a **boolean**. This lesson shows what is true and false in Python, and how to combine conditions. These rules are small, but they cause many bugs and many interview questions.

## `bool`: True and False

`bool` has only two values: `True` and `False`. (Remember from lesson 2: Python treats them as `1` and `0`, so `True == 1`.)

Comparisons give a `bool`:

```python
5 > 3      # -> True
5 == 5     # -> True   == asks "are these equal?"
5 != 5     # -> False  != means "not equal"
3 <= 2     # -> False
```

The six comparison operators are `==  !=  <  <=  >  >=`. You can **chain** them, which is nice for checking a range:

```python
age = 25
18 <= age < 60     # -> True   means (18 <= age) and (age < 60)
1 < 3 > 2          # -> True   means (1 < 3) and (3 > 2)
```

Strings are compared letter by letter, using each letter's code. Capital letters come before small letters:

```python
"apple" < "banana"   # -> True
"Z" < "a"            # -> True
```

Comparing different kinds of values with `<` is a `TypeError`. `==` just says `False`:

```python
1 == "1"    # -> False
1 < "2"     # TypeError: '<' not supported between instances of 'int' and 'str'
```

## Truthiness: what counts as true?

Python can use **any** value as a condition, not only `True` and `False`. These values count as **falsy** (they act like `False`). Everything else is **truthy** (it acts like `True`):

| Falsy values |
|---|
| `False` and `None` |
| `0` and `0.0` |
| empty things: `""`, `[]`, `()`, `{}`, `set()` |

```python
bool(0)        # -> False
bool(0.0)      # -> False
bool("")       # -> False
bool("0")      # -> True    a string with a character in it, even "0"
bool(" ")      # -> True    a space is a character too
bool([0])      # -> True    a list with one item
```

So you can write short checks:

```python
items = []
if not items:           # same as: if len(items) == 0
    print("empty")      # -> empty
```

(You will learn `if` in lesson 6.)

## `and`, `or`, `not`

- `not x` flips `True` and `False`.
- `a and b` is true when **both** are true.
- `a or b` is true when **at least one** is true.

```python
not True             # -> False
True and False       # -> False
True or False        # -> True
```

There is one surprise. `and` and `or` do not always give `True` or `False`. They give back **one of the two values you gave them**:

| Expression | Gives |
|---|---|
| `a or b` | `a` if `a` is truthy, otherwise `b` |
| `a and b` | `a` if `a` is falsy, otherwise `b` |

```python
"Dev" or "guest"    # -> 'Dev'     "Dev" is truthy, so we get it
"" or "guest"       # -> 'guest'   "" is falsy, so we get the other one
[1] and "yes"       # -> 'yes'
0 and "yes"         # -> 0
```

This gives a neat trick for a default value. If the name is empty, use `"guest"`:

```python
name = ""
shown = name or "guest"
print(shown)    # -> guest
```

### Short-circuiting

Python stops as soon as it knows the answer. `and` stops at the first falsy value. `or` stops at the first truthy value. The rest is never run.

```python
0 and 1 / 0       # -> 0    1 / 0 is never run, so there is no error
1 or 1 / 0        # -> 1
```

This protects you from errors. In a check like `isinstance(x, float) and 0 <= x <= 1`, the second part only runs when `x` really is a float, so `0 <= x` can never fail with a `TypeError`.

Here is a step-by-step example. A valid score is a float from 0 to 1.

1. First check the type: `isinstance(x, float)`.
2. Then check the range: `0 <= x <= 1`.
3. Join the two checks with `and`.

```python
x = 0.8
isinstance(x, float) and 0 <= x <= 1    # -> True
x = "0.8"
isinstance(x, float) and 0 <= x <= 1    # -> False  (the range check never runs)
```

## `in` and `is`

```python
3 in [1, 2, 3]            # -> True
"k" in {"a": 1}           # -> False   on a dict, `in` checks the keys
"k" not in {"a": 1}       # -> True
x = None
x is None                 # -> True
x is not None             # -> False
```

You will learn lists in lesson 8 and dicts in lesson 11.

## Which goes first? (precedence)

When you mix operators, Python follows an order, like in maths (multiply before add). From first to last:

1. `**`
2. `-x` (minus sign)
3. `*  /  //  %`
4. `+  -`
5. comparisons, `in`, `is`
6. `not`
7. `and`
8. `or`

```python
True or False and False     # -> True    and goes first: True or (False and False)
not 1 == 2                  # -> True    not (1 == 2)
-2 ** 2                     # -> -4      -(2 ** 2)
```

When you are not sure, add parentheses. They make the code easier to read:

```python
(True or False) and False   # -> False
```

## Common mistakes

- Writing `if x == True:`. Just write `if x:`.
- Writing `if name == "a" or "b":`. This is always true, because it means `(name == "a") or "b"`, and `"b"` is truthy. Write `name in ("a", "b")` instead.
- Using `value or default` when `0` or `""` are real values. `requested or 20` turns `0` into `20`.
- Expecting `"a" and "b"` to be `True`. It is `'b'`.

## A little deeper (optional)

**The `or` default trap.** Because `or` looks at truthiness, a real `0` is replaced:

```python
def page_size(requested):
    return requested or 20

page_size(50)   # -> 50
page_size(0)    # -> 20   0 is falsy. Maybe not what you wanted!
```

When `0`, `""` or `[]` are valid values, check `is None` explicitly (you will write that with `if` in the next lesson).

**`is True`.** `if x is True:` is only right when you need the exact `True` object. Most of the time `if x:` is better.

## Summary

- Falsy values: `False`, `None`, zero, and empty things. Everything else is truthy.
- Comparisons can chain: `a < b < c`.
- `and` and `or` give back one of their values, and they stop early (short-circuit). `not` always gives a `bool`.
- `in` checks if something is inside (the keys, for a dict). `is` checks if it is the same value.
- Order: arithmetic, then comparisons, then `not`, then `and`, then `or`. Use parentheses when unsure.
