---
title: Context managers
summary: Make sure setup and cleanup always happen with `with`. Learn how it works for files, locks and transactions, and how to write your own.
plan_ids: [PY-04]
---

Some things must always be cleaned up: files must be closed, locks must be released, and database changes must be saved (committed) **or** undone (rolled back). If you forget, the problems often appear only when many people use your app. The `with` statement does the cleanup for you, **even when an error happens**.

## `with` in practice

You have already used it for files:

```python
with open("data.txt") as f:
    content = f.read()
# f is closed here, even if read() raised an error
```

Without `with`, you would have to write this:

```python
f = open("data.txt")
try:
    content = f.read()
finally:
    f.close()
```

Many things work with `with`: files, locks (`threading.Lock()`), database sessions, HTTP clients, temporary folders, and `pytest.raises(...)`.

You can open several in one line:

```python
with open("in.txt") as src, open("out.txt", "w") as dst:
    dst.write(src.read())
```

## How `with` works: `__enter__` and `__exit__`

An object that works with `with` is a **context manager**. It has two special methods:

- `__enter__` runs at the start. What it returns goes to the name after `as`.
- `__exit__` runs at the end, **always**: after normal finish, after an error, after a `return` or a `break`.

```python
class Announce:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        print("start", self.name)
        return self                          # this goes to the name after "as"

    def __exit__(self, exc_type, exc, tb):
        print("end", self.name)
        return False                         # do not hide errors

with Announce("job") as a:
    print("working on", a.name)
# -> start job
# -> working on job
# -> end job
```

`__exit__` gets three values: the type, the value and the traceback of the error. If the block finished without an error, all three are `None`.

What `__exit__` returns matters:

- Returning `False` (or `None`) lets the error continue (it **propagates**). This is what you almost always want.
- Returning a **truthy** value **hides** (suppresses) the error. Do this only on purpose.

```python
class IgnoreErrors:
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        return True            # hides any error

with IgnoreErrors():
    1 / 0                      # no error is shown
print("still running")         # -> still running
```

## Writing one the easy way: `@contextmanager`

Writing a class is a lot of code. With `@contextmanager` from `contextlib`, you write a **generator** (lesson 22) with exactly one `yield`.

- The code **before** the `yield` is the setup.
- The code **after** the `yield` is the cleanup.
- The value you `yield` goes to the name after `as`.

```python
from contextlib import contextmanager

@contextmanager
def section(title):
    print("==", title)
    try:
        yield                    # the code inside the with-block runs here
    finally:
        print("== done")         # always runs

with section("report"):
    print("inside")
# -> == report
# -> inside
# -> == done
```

If the code inside the `with` block raises an error, the error comes out **at the `yield`**. So put the cleanup in `finally`, as above. Without `try/finally`, the cleanup would be skipped when there is an error.

## Undo on error (the idea behind transactions)

A **transaction** is a group of changes that must happen **all together or not at all**. It has two endings:

- **commit**: everything worked, keep the changes.
- **rollback**: something failed, undo the changes.

A context manager is perfect for this. A step-by-step example without a database. We edit a list, and if an error happens, we put it back as it was:

1. Save a copy before the block.
2. `yield` so the block can edit the list.
3. If there is an error, restore the copy, and **raise the error again** so the caller knows.

```python
@contextmanager
def undo_on_error(items):
    backup = list(items)         # a copy
    try:
        yield items
    except Exception:
        items[:] = backup        # put the old content back
        raise                    # do not hide the error
    # no error: the changes stay (this is the "commit")

data = [1, 2, 3]
try:
    with undo_on_error(data) as d:
        d.append(4)
        raise ValueError("oops")
except ValueError:
    pass
print(data)    # -> [1, 2, 3]     the append was undone
```

A real database version has the same shape: begin, `yield`, commit if all is fine, roll back and re-raise if there is an error. The error must not be hidden. A rollback that hides the error means nobody finds out that something failed.

> You will use exactly this pattern with database sessions in the FastAPI track.

## Putting a value back: environment variables

**Environment variables** are settings that live outside your code. In Python, `os.environ` works like a dict:

```python
import os

os.environ["MODE"] = "test"          # set
print(os.environ.get("MODE"))        # -> test
print(os.environ.get("NOPE"))        # -> None   a missing name is None with .get
os.environ.pop("MODE", None)         # remove (no error if missing)
```

A "set it for a while, then put the old value back" tool is a classic context manager. The idea is always the same:

1. In `__enter__`: remember the old value, then set the new one.
2. In `__exit__`: put the old value back, even if there was an error.

For several names, you can collect keyword arguments with `**` (lesson 13), so `my_cm(A="1", B="2")` gives you the dict `{"A": "1", "B": "2"}`.

Remember that a name that did not exist before must be **removed** at the end, not set to `None`.

## Timing a block

`time.perf_counter()` gives the time in seconds. A context manager can measure a block. A class version stores the start in `__enter__` and the result in `__exit__`, so you can read it after the `with`:

```python
import time

class Stopwatch:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.seconds = time.perf_counter() - self.start
        return False

with Stopwatch() as w:
    sum(range(1_000_000))
print(w.seconds < 1)      # -> True
```

Because `__exit__` always runs, `w.seconds` is set even if the block raised an error.

## More tools in `contextlib`

| Tool | What it does |
|---|---|
| `suppress(FileNotFoundError)` | ignores the listed errors inside the block |
| `closing(obj)` | calls `obj.close()` at the end |
| `ExitStack()` | handles a number of context managers that is not known in advance |
| `nullcontext()` | does nothing (a placeholder) |

```python
from contextlib import suppress

with suppress(FileNotFoundError):
    os.remove("cache.tmp")        # no error if the file is missing
```

## A little deeper (optional)

**Async context managers.** `async with` uses `__aenter__` and `__aexit__` for things that need `await`, like an async HTTP client:

```python
async with httpx.AsyncClient() as client:
    r = await client.get(url)
```

FastAPI's app **lifespan** is an async context manager: the code before the `yield` runs at startup, and the code after runs at shutdown. You will see it in the FastAPI track. A `yield` dependency (like a database session) works the same way.

## Common mistakes

- Opening files or clients without `with`, so they are never closed.
- Writing a `@contextmanager` without `try/finally`, so the cleanup is skipped when there is an error.
- Returning `True` from `__exit__` by accident, and hiding errors.
- Using more than one `yield` in a `@contextmanager`.
- After a rollback, hiding the error instead of raising it again.

## Interview corner

- **Q: What does `with` guarantee?** `__exit__` runs however the block ends: normally, with an error, with `return` or with `break`.
- **Q: How would you write a database transaction helper?** A context manager that begins, yields, commits on success, and rolls back and re-raises on an error.
- **Q: How can `__exit__` suppress an error?** By returning a truthy value.
- **Q: Where does FastAPI use context managers?** In the `lifespan` function for startup and shutdown, and in `yield` dependencies such as database sessions.

## Summary

- `with` guarantees cleanup. Use it for every resource.
- A context manager has `__enter__` (setup, its result goes to `as`) and `__exit__` (cleanup). A truthy return from `__exit__` hides the error.
- `@contextmanager` turns a generator with one `yield` into a context manager. Use `try/finally` around the `yield`.
- Transactions: commit on success, roll back on error, and raise the error again.
- `async with` is for async resources. FastAPI's lifespan uses it.
