# 12. Context managers

You have written `with open(...) as f:` since chapter 6. Now we look inside. A **context manager** is any object that does **setup** when you enter a `with` block and **cleanup** when you leave it, no matter how you leave: normally, by `return`, or by an error.

## The problem it solves

Some things must always be undone: close a file, release a lock, end a database transaction, disconnect. If you write the cleanup by hand, an error in the middle can skip it:

```python
f = open("data.txt", "w")
f.write("hi")
# if an error happens here, close() is never reached
f.close()
```

With `try/finally` it is safe but long. `with` is the short, safe form of exactly that.

## How `with` works

```python
class Timer:
    def __enter__(self):
        print("enter")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("exit", exc_type.__name__ if exc_type else None)
        return False

with Timer():
    print("body")
# -> enter
# -> body
# -> exit None
```

Two special methods make a context manager:

- `__enter__` runs at the start. What it returns is the name after `as`.
- `__exit__` runs at the end, **always**. It receives the error (type, value, traceback) if one happened, or `None`s if not.

If an error happens inside, `__exit__` still runs first, then the error continues:

```python
try:
    with Timer():
        raise ValueError("x")
except ValueError:
    print("caught")
# -> enter
# -> exit ValueError
# -> caught
```

If `__exit__` returns `True`, it **swallows** the error. Return `False` (or nothing) to let it go on. Swallowing errors silently is rarely wise.

## The easy way: `@contextmanager`

Writing a class is long. The `contextlib` module lets you write a context manager as a **generator** (chapter 10): everything before `yield` is setup, everything after is cleanup.

```python
from contextlib import contextmanager

@contextmanager
def tag(name):
    print(f"<{name}>")
    try:
        yield
    finally:
        print(f"</{name}>")

with tag("b"):
    print("text")
# -> <b>
# -> text
# -> </b>
```

The `try/finally` around `yield` makes sure the cleanup runs even if the body fails. A value after `yield` becomes the `as` variable: `yield connection`. You will see this pattern in database code: open a session, `yield` it, close it afterwards. FastAPI's `yield` dependencies work the same way.

## Handy tools

`suppress` ignores one kind of error on purpose:

```python
from contextlib import suppress

with suppress(FileNotFoundError):
    open("nope.txt")
print("ok")
# -> ok
```

You can open several in one line: `with open("a") as src, open("b", "w") as dst:`. For async code there is `async with`, which uses `__aenter__` and `__aexit__` (chapter 15).

::: {.box .checkpoint}
**Checkpoint:** you can say what `__enter__` and `__exit__` do, and write a `@contextmanager` that prints before and after a block.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Forgetting the `try/finally` around `yield`, so cleanup is skipped on error.
- Returning `True` from `__exit__` and hiding real bugs.
- Using the resource after the `with` block has closed it.
- Using `yield` twice in a `@contextmanager`.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: What is a context manager?** An object with `__enter__` and `__exit__` that guarantees setup and cleanup around a block.

**Q: Why use `with` for files?** It closes the file even if an error occurs.

**Q: How do you write one quickly?** With `@contextlib.contextmanager` on a generator that yields once.

**Q: What does returning `True` from `__exit__` do?** It suppresses the exception.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Write a `@contextmanager` named `timer` that prints how long its block took.
2. Write a class-based context manager that changes the current folder (`os.chdir`) and restores it at exit.
3. Use `suppress` to delete a file only if it exists.
4. Show that cleanup runs even when the body raises an error.
5. **Think:** how is a database session in FastAPI (`yield session`) a context manager?
:::
