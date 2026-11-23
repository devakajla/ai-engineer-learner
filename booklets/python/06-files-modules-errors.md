# 6. Files, modules and errors

Real programs read and write files, split code across several files, and must survive things going wrong. This chapter covers all three.

## Part 1: files

Programs forget everything when they stop. Files are how data **lasts**: a saved note, a config, a log.

### The easy way: `pathlib`

A **path** is the address of a file. `Path` is a tidy object for working with paths.

```python
from pathlib import Path

p = Path("notes.txt")
p.write_text("hi\nthere\n")
print(p.read_text().splitlines())
# -> ['hi', 'there']
print(p.exists())
# -> True
```

`write_text` creates the file (or overwrites it). `read_text` reads everything at once. `splitlines` cuts the text into a list of lines. Use `Path` for small files, and it is the modern way to build paths: `Path("data") / "file.txt"`.

### `with open(...)`: for loops and big files

```python
with open("notes.txt") as fh:
    for line in fh:
        print(line.strip())
# -> hi
# -> there
```

Why `with`? A file is a resource that must be **closed** when you finish, otherwise data may not be saved and the operating system keeps it busy. `with` closes it for you, even if an error happens inside. Always open files with `with`.

The second argument is the **mode**:

| Mode | Meaning |
| --- | --- |
| `"r"` | read (default) |
| `"w"` | write, and **erase** what was there |
| `"a"` | append to the end |

Looping over `fh` reads **one line at a time**, so even a huge file does not fill your memory. Each line keeps its `\n` at the end, which is why we call `.strip()`.

### JSON: saving structured data

JSON is a text format for dicts, lists, strings, numbers and booleans. It is the language of web APIs.

```python
import json

text = json.dumps({"a": [1, 2], "b": None})
print(text)
# -> {"a": [1, 2], "b": null}
print(json.loads('{"x": 1}'))
# -> {'x': 1}
```

Memory trick: `dumps` = "dump to **s**tring", `loads` = "load from **s**tring". Without the `s` (`dump`, `load`) they work with files. Python `None` becomes JSON `null`.

## Part 2: modules

A **module** is just a `.py` file. When your program grows, you split it into files, and use `import` to reach code in another file or in a library.

```python
import math
from pathlib import Path
from collections import Counter as C

print(math.sqrt(16))
# -> 4.0
```

Three forms: `import math` (use as `math.sqrt`), `from x import y` (use `y` directly) and `import x as z` (give it a short name). Python ships with a huge **standard library** (`math`, `json`, `pathlib`, `datetime`, `random`...). Libraries from the internet are installed with `uv add name` (the quick reference lists the most useful ones).

Your own file `helpers.py` with a function `add` is used from `main.py` as `from helpers import add`.

### `if __name__ == "__main__":`

You will see this at the bottom of many files. When a file is **run directly**, Python sets a special name `__name__` to `"__main__"`. When the file is only **imported**, `__name__` is the module's name. So the block runs only on direct run, which lets one file be both a program and a library.

```python
def main():
    print("running")

if __name__ == "__main__":
    main()
```

## Part 3: errors

Errors will happen: a missing file, bad user input, a network that is down. The question is not "how to avoid them" but "what should happen when they come". Python's tool is the **exception**.

When something goes wrong, Python **raises** an exception, which jumps out of the current code and travels upward until someone **catches** it. If nobody does, the program stops with a message.

### `try` / `except`

```python
try:
    int("abc")
except ValueError as error:
    print("ValueError:", error)
# -> ValueError: invalid literal for int() with base 10: 'abc'
```

The risky code goes in `try`. If it raises a `ValueError`, Python runs the `except` block instead of crashing. `as error` gives you the exception object so you can show its message.

The full form has two more parts:

```python
try:
    1 / 0
except ZeroDivisionError:
    print("zero")
else:
    print("no error")
finally:
    print("always")
# -> zero
# -> always
```

`else` runs only if there was **no** error. `finally` runs **always**, error or not, so it is the place for cleanup. Catch **specific** exceptions. A bare `except:` hides real bugs, including typos.

Common exceptions you will meet: `ValueError` (right type, bad value), `TypeError` (wrong type), `KeyError` (missing dict key), `IndexError` (list position too big), `FileNotFoundError`, `ZeroDivisionError`.

### Raising your own

```python
def set_age(age):
    if age < 0:
        raise ValueError("age cannot be negative")
    return age
```

`raise` stops the function and sends the error to the caller. A function should **raise** when it cannot do its job, rather than return a fake value like `-1`.

### Custom exceptions

For your own application, make your own error types by inheriting from `Exception`. (Inheriting means "is a kind of". The next chapters explain it fully.)

```python
class AppError(Exception):
    pass

class NotFound(AppError):
    def __init__(self, item_id):
        super().__init__(f"id {item_id} not found")
        self.item_id = item_id

try:
    raise NotFound(5)
except AppError as error:
    print(type(error).__name__, error, error.item_id)
# -> NotFound id 5 not found 5
```

Why this is good: `NotFound` is a kind of `AppError`, so one `except AppError` catches every error of yours, while other code can still catch the exact `NotFound`. In FastAPI (that booklet), these errors are turned into HTTP responses.

### Chaining: keep the original cause

```python
try:
    try:
        int("x")
    except ValueError as error:
        raise AppError("bad input") from error
except AppError as error:
    print(repr(error.__cause__))
# -> ValueError("invalid literal for int() with base 10: 'x'")
```

`raise ... from error` links the new error to the old one, so the cause shows in the traceback. Use it when you translate a low-level error to your own.

### Style: EAFP

Python prefers "**E**asier to **A**sk **F**orgiveness than **P**ermission": just try, and handle the failure, instead of checking first. Example: instead of checking whether a file exists and then opening it (the file may disappear between the two lines), open it and catch `FileNotFoundError`.

::: {.box .checkpoint}
**Checkpoint:** you can read a file line by line with `with`, explain `dumps` vs `dump`, say when `finally` runs, and make a custom exception.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Opening a file without `with`, and never closing it.
- Using mode `"w"` on a file you meant to add to. It **erases** it.
- A bare `except:` that swallows every error.
- Catching an error and doing nothing (`pass`). The bug becomes invisible.
- Returning `-1` or `None` for failure instead of raising.
- Forgetting that `line` from a file ends with `\n`.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: What does `with` do?** It runs setup and guaranteed cleanup (closing the file), even if an error happens.

**Q: `else` and `finally` in `try`?** `else` runs when no exception happened. `finally` always runs.

**Q: Why custom exceptions?** They name your failure cases, let callers catch exactly what they care about, and group errors by a base class.

**Q: What is `if __name__ == "__main__"` for?** It runs code only when the file is executed directly, not when imported.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Write lines to `todo.txt` with `"w"`, add one more with `"a"`, then read and print them numbered.
2. Count how many lines a file has without loading it all at once.
3. Save a dict to `data.json` and load it back. Check that both are equal.
4. Write `safe_int(text)` that returns `None` for bad input instead of crashing.
5. Read a file that does not exist and print a friendly message.
6. Create `AppError` and `NotFound` as above and catch `NotFound` as `AppError`.
7. **Think:** why is `except:` (with nothing after it) dangerous?
:::
