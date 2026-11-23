---
title: Error handling deep
summary: The exception family tree, full try statements, your own error classes, keeping the cause with raise from, and retrying flaky calls.
plan_ids: [PY-07]
---

In Level 1 you learned `try` and `except`. Real programs need more: **your own error types**, keeping the original cause of an error, cleaning up reliably, and **retrying** calls that fail sometimes (network and AI APIs fail a lot).

## The exception family tree

Exceptions are classes, and they form a family tree. A child is a more specific kind of its parent.

```
BaseException
├── SystemExit, KeyboardInterrupt      ← do not catch these
└── Exception                          ← catch from here down
    ├── ValueError, TypeError, KeyError, IndexError, ...
    ├── OSError
    │   ├── FileNotFoundError, PermissionError
    │   └── ConnectionError
    ├── TimeoutError
    └── your own errors
```

`except X` also catches all **children** of X. So **the order matters**: put the specific handlers first. Python uses the first one that matches.

```python
try:
    open("missing.txt")
except FileNotFoundError:      # specific: first
    print("no such file")      # -> no such file
except OSError:                # broader: after
    print("other OS problem")
```

If you swapped them, the `OSError` handler would catch the `FileNotFoundError` first (a `FileNotFoundError` **is an** `OSError`), and the specific handler would never run.

Never write a bare `except:`. It catches even `KeyboardInterrupt` (`Ctrl+C`). If you need a catch-all at the edge of your program, write `except Exception:` and **log it**.

## The full `try` statement

```python
try:
    conn = connect()
except ConnectionError as e:
    print("connect failed:", e)
    raise
else:
    rows = conn.fetch()      # runs only if NO error happened
finally:
    cleanup()                # ALWAYS runs
```

- Keep the `try` block **small**, so you do not catch errors from unrelated lines.
- `else` is the success-only part.
- `finally` always runs: after success, after an error, and even before a `return`.
- A bare `raise` in an `except` block raises the same error again, with its traceback.

`finally` and `return` together:

```python
def f():
    try:
        return "try"
    finally:
        print("cleanup")    # runs BEFORE the function really returns

print(f())
# -> cleanup
# -> try
```

For closing files and connections, a `with` statement (lesson 24) is usually better than `finally`.

## Your own exceptions

A custom exception is a class that inherits from `Exception`. Usually you make **one base class** for your app, and children for each kind of problem.

```python
class AppError(Exception):
    """Base for all errors raised by our app."""
    status_code = 500           # a class attribute with a default

class NotFoundError(AppError):
    status_code = 404

    def __init__(self, resource, resource_id):
        super().__init__(f"{resource} {resource_id} not found")   # this becomes str(error)
        self.resource = resource
        self.resource_id = resource_id

class ConflictError(AppError):
    status_code = 409

e = NotFoundError("Task", 7)
print(e)                              # -> Task 7 not found
print(e.status_code)                  # -> 404
print(isinstance(e, AppError))        # -> True
```

Why use a family of your own errors?

- Callers can catch **all** your errors with `except AppError`, or just one kind.
- Errors can carry **data** (like `resource` and `resource_id`). A web framework can turn a `NotFoundError` into a clean 404 response (you will see this in the FastAPI track).
- Your business logic stays free from web details.

Errors can have methods too. Add a `to_dict()` to the base class, and every child gets it. A child can also **extend** it with `{**super().to_dict(), "field": self.field}`, which copies the parent's dict and adds a new key.

```python
class AppError(Exception):
    def to_dict(self):
        return {"error": type(self).__name__, "message": str(self)}

class FieldError(AppError):
    def __init__(self, field, message):
        super().__init__(f"{field}: {message}")
        self.field = field

    def to_dict(self):
        return {**super().to_dict(), "field": self.field}

print(FieldError("age", "too big").to_dict())
# -> {'error': 'FieldError', 'message': 'age: too big', 'field': 'age'}
```

## Keep the cause: `raise ... from ...`

Often you catch a low-level error and raise a clearer error of your own. Use `from` so the original error is **not lost**:

```python
import json

class ConfigError(Exception):
    pass

def load_config(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ConfigError("config is not valid JSON") from e

try:
    load_config("{oops")
except ConfigError as err:
    print(err)                    # -> config is not valid JSON
    print(type(err.__cause__))    # -> <class 'json.decoder.JSONDecodeError'>
```

The traceback now shows both errors, and `err.__cause__` holds the original. Use `from None` when you want to hide the cause on purpose.

Notice that each `try` block holds only the one risky call. This makes it clear which error came from where.

## Retrying flaky calls

Network calls sometimes fail for a short time (a timeout, "429 too many requests", "503 service unavailable"). Trying again often works. But do not retry in a tight loop. That hits the server again and again. Wait a bit longer after each failure. This is **exponential backoff**: 0.5s, then 1s, then 2s, and so on.

A step-by-step plan:

1. Call the function. If it works, return the result.
2. If it fails with a **retry-able** error and you have tries left, wait, then try again.
3. If you are out of tries, let the error go up (`raise`).
4. Any other error should stop at once. Do not retry it.

```python
import time

def call_with_retry(fn, tries=3, wait=0.5):
    while True:
        try:
            return fn()
        except (ConnectionError, TimeoutError):
            tries -= 1
            if tries == 0:
                raise                  # out of tries: let the error go up
            time.sleep(wait)
            wait *= 2                  # 0.5 -> 1 -> 2 ...
```

Rules for retrying:

- Retry only **transient** problems (network, 429, 5xx). Never retry a validation error (422) or a bug in your code. It will fail again.
- Only retry actions that are safe to repeat (**idempotent**).
- Limit the number of tries.
- Add a small **random delay** (jitter) so many clients do not all retry at exactly the same moment.

Libraries like `tenacity` do this for you. Knowing the idea is what interviews test.

## Logging errors

```python
import logging
log = logging.getLogger(__name__)

try:
    process()
except Exception:
    log.exception("processing failed")   # logs the message and the full traceback
    raise
```

Never write `except Exception: pass`. Silent failures are the hardest bugs to find.

## A little deeper (optional)

**EAFP and LBYL.** Python usually prefers "try it and handle the failure" (EAFP) over "check first" (LBYL). It avoids races (a file can disappear between your check and your open). When the failure is common and easy to check, a simple `if` is fine.

**Exception groups (Python 3.11+).** When several tasks fail at once, Python can raise an `ExceptionGroup`. You handle the parts with `except*`:

```python
try:
    ...
except* ConnectionError as group:
    ...
```

You will meet this in the asyncio lesson.

## Common mistakes

- A bare `except:` or `except Exception: pass`.
- A huge `try` block that hides where the error came from.
- Losing the original error when you wrap it (forgetting `from e`).
- Retrying errors that are not temporary, or retrying with no waiting.
- Putting a broad handler before a specific one, so the specific one never runs.

## Interview corner

- **Q: What is the difference between `else` and `finally` in a `try`?** `else` runs only if there was no error. `finally` always runs.
- **Q: Why write `raise NewError(...) from e`?** It keeps the original error as `__cause__`, which helps debugging.
- **Q: How would you retry calls to an unreliable API?** Retry only temporary errors (timeouts, 429, 5xx) with a limited number of tries and exponential backoff plus jitter. Keep the call safe to repeat.
- **Q: Why create your own exception classes?** To have clear, catchable errors that carry data, and to keep business logic separate from the web layer.

## Summary

- `except` also catches children. Put specific handlers before general ones.
- `try` / `except` / `else` / `finally`. Keep `try` small. A bare `raise` raises the same error again.
- Build a family of your own errors with a common base class, and put data on them.
- `raise X from e` keeps the cause.
- Retry only temporary, repeatable calls, with backoff, a limit and jitter.
