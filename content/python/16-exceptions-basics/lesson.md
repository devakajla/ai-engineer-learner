---
title: Exceptions basics
summary: Learn what errors look like in Python, how to read them, how to handle them with try/except, and how to raise your own.
plan_ids: [PY-07]
---

Sometimes things go wrong: the user types bad input, a file is missing, or you divide by zero. When this happens, Python **raises an exception**. If nothing handles it, the program stops and prints a message called a **traceback**.

Good code handles the errors it can expect, and lets the surprising ones stop the program loudly, so you can fix them.

## Reading a traceback

```python
def divide(a, b):
    return a / b

divide(1, 0)
```

```
Traceback (most recent call last):
  File "demo.py", line 4, in <module>
    divide(1, 0)
  File "demo.py", line 2, in divide
    return a / b
ZeroDivisionError: division by zero
```

Read it **from the bottom**. The last line says what went wrong: the error type (`ZeroDivisionError`) and a message. The lines above show the path the code took to get there.

## `try` and `except`

Put the risky code in `try`. Put the plan B in `except`.

```python
try:
    n = int("abc")
except ValueError:
    n = 0
print(n)   # -> 0
```

Python runs the `try` block. If it raises a `ValueError`, Python jumps to the `except` block. If nothing goes wrong, the `except` block is skipped.

A step-by-step example. Turn text into a decimal number, or give back a default when the text is not a number:

1. Put the conversion in `try`.
2. Catch the error that `float()` raises for bad text: `ValueError`.
3. In `except`, give back the default.

```python
def safe_float(text, default=0.0):
    try:
        return float(text)
    except ValueError:
        return default

safe_float("2.5")      # -> 2.5
safe_float("hello")    # -> 0.0
```

### Get the error message

Add `as e` to get the error object. Printing it shows the message:

```python
try:
    int("abc")
except ValueError as e:
    print("bad input:", e)   # -> bad input: invalid literal for int() with base 10: 'abc'
```

### Handle different errors differently

You can have several `except` blocks. Python uses the first one that matches.

```python
def parse(text):
    try:
        return 100 / int(text)
    except ValueError:
        return "not a number"
    except ZeroDivisionError:
        return "zero not allowed"

parse("5")     # -> 20.0
parse("x")     # -> 'not a number'
parse("0")     # -> 'zero not allowed'
```

To handle several types the same way, put them in a tuple: `except (ValueError, TypeError):`.

## `else` and `finally`

```python
try:
    value = int("42")
except ValueError:
    print("bad")
else:
    print("ok", value)      # runs only if there was NO error  -> ok 42
finally:
    print("always runs")    # runs in every case               -> always runs
```

- `else` holds the code that should run only when everything worked. It keeps the `try` block small.
- `finally` holds the cleanup that must always happen. It runs even if the `try` block does a `return`.

## Keep `try` small and `except` specific

```python
# bad: hides every bug
try:
    do_everything()
except:
    pass

# good: catch only what you expect
try:
    n = int(text)
except ValueError:
    n = 0
```

- Never write a bare `except:`. It even catches `Ctrl+C`.
- Never silently `pass`. Nobody will know something failed. At least log the error.
- Put only the risky line in `try`, not the whole function.

## `raise`: signal your own errors

You can raise an error yourself when something is wrong. This stops the function and sends the error to the code that called it.

```python
def set_age(age):
    if age < 0:
        raise ValueError("age cannot be negative")
    return age

set_age(-1)   # ValueError: age cannot be negative
```

You can also catch one error and raise a clearer one of your own:

```python
def parse_count(text):
    try:
        count = int(text)
    except ValueError:
        raise ValueError("count must be a number")
    if count < 0:
        raise ValueError("count cannot be negative")
    return count

parse_count("7")     # -> 7
parse_count("abc")   # ValueError: count must be a number
parse_count("-2")    # ValueError: count cannot be negative
```

A bare `raise` inside an `except` block raises the same error again. Use it after you log the problem:

```python
try:
    int("x")
except ValueError:
    print("logging the problem")
    raise
```

## Common exceptions

| Exception | Typical cause |
|---|---|
| `ValueError` | right type, wrong value: `int("abc")` |
| `TypeError` | wrong type: `"a" + 1` or `"1" / 2` |
| `KeyError` | missing dict key: `d["x"]` |
| `IndexError` | list index out of range |
| `AttributeError` | wrong attribute, like `None.upper()` |
| `ZeroDivisionError` | `1 / 0` |
| `FileNotFoundError` | `open("nope.txt")` |
| `ImportError` | module not found |

## A little deeper (optional)

**EAFP and LBYL.** There are two styles. **LBYL** means "look before you leap": check first. **EAFP** means "it is easier to ask forgiveness than permission": just try, and handle the failure. Python programmers often like EAFP.

```python
data = {"age": 30}

# LBYL: check first
if "age" in data:
    age = data["age"]

# EAFP: try, then handle
try:
    age = data["age"]
except KeyError:
    age = None
```

Both are fine. If a simple check exists (`in`, `.get`), use it. Use `try` when checking is as hard as the work itself (files, converting text).

**Files and errors.**

```python
try:
    with open("config.json", encoding="utf-8") as f:
        text = f.read()
except FileNotFoundError:
    text = "{}"
```

**Families.** Exceptions have a family tree. `KeyError` and `IndexError` are both kinds of `LookupError`, and most errors are kinds of `Exception`. Level 2 teaches custom exceptions and more.

## Common mistakes

- Using a bare `except:` or `except Exception: pass`. It hides bugs.
- Putting a lot of code inside `try`, so you catch errors you did not expect.
- Catching an error, printing something, and carrying on as if nothing happened.
- Using exceptions when a simple `if` would be clearer.
- Raising `Exception("...")` instead of a specific type like `ValueError`.
- Forgetting that `finally` runs even after a `return`.

## Summary

- Read a traceback from the bottom: the error type and message come first.
- `try` / `except Type as e` / `else` / `finally`.
- Catch specific errors, keep `try` small, and never hide errors silently.
- `raise ValueError("message")` signals bad input. A bare `raise` raises the same error again.
- Know the common errors: `ValueError`, `TypeError`, `KeyError`, `IndexError`, `AttributeError`, `ZeroDivisionError` and `FileNotFoundError`.
