---
title: Type hints
summary: Add labels to your code so editors, checkers and FastAPI know what each value is - unions, generics, Literal, TypedDict, Protocol and Annotated.
plan_ids: [PY-05]
---

A **type hint** is a label that says what kind of value a name or a function should use. Python itself **ignores** hints when the program runs. But other tools read them:

- Your editor uses them for autocomplete.
- A **type checker** (like mypy or pyright) finds bugs before you run the code.
- **FastAPI and Pydantic** read them while the app runs, to check and convert data. In FastAPI, type hints are not decoration. They are the API.

## The basics

The form is `name: type`. For a function result, write `-> type`.

```python
def greet(name: str, times: int = 1) -> str:
    return ", ".join([f"Hello {name}"] * times)

count: int = 0
tags: list[str] = []                 # a list of strings
scores: dict[str, float] = {}        # keys are str, values are float
point: tuple[int, int] = (1, 2)      # exactly two ints
values: tuple[int, ...] = (1, 2, 3)  # any number of ints
unique: set[str] = set()
```

Write `list[str]`, `dict[str, int]` and so on. (Old code uses `typing.List` and `typing.Dict`. Do not use them in new code.)

## Hints are NOT checked when the program runs

```python
def add(a: int, b: int) -> int:
    return a + b

print(add("x", "y"))      # -> xy       Python does not care!
```

Hints are checked only by a type checker or by a tool like Pydantic. You can read them yourself with `typing.get_type_hints`:

```python
from typing import get_type_hints

print(get_type_hints(add))
# -> {'a': <class 'int'>, 'b': <class 'int'>, 'return': <class 'int'>}
```

## Optional values and unions

A **union** means "one of these types". Write it with `|`. The common case is "a value or `None`":

```python
def find_user(users: dict[int, str], user_id: int) -> str | None:
    return users.get(user_id)          # .get gives None when missing
```

A parameter that may be `None`:

```python
def greet(name: str | None = None) -> str:
    return f"Hello {name or 'friend'}"
```

Do **not** write `name: str = None`. That hint says "always a string", but the default is `None`, so the hint lies.

A type checker makes you handle `None` before using the value:

```python
user = find_user({1: "ana"}, 5)
# user.upper()           # a checker complains: user may be None
if user is not None:
    print(user.upper())   # fine here: it is a str now
```

## `Any` and `object`

- `Any` switches type checking **off** for that value. Use it rarely (for example for raw JSON).
- `object` accepts any value, but you can do almost nothing with it until you check its type with `isinstance`. This is safer.

## Hints for functions

A function that takes another function is written with `Callable[[argument types], result type]`. Import `Callable` and `Iterable` from `collections.abc`:

```python
from collections.abc import Callable, Iterable

def apply_all(fn: Callable[[int], str], items: Iterable[int]) -> list[str]:
    return [fn(i) for i in items]

print(apply_all(str, [1, 2]))    # -> ['1', '2']
```

`Callable[[int], str]` reads: "a function that takes one `int` and gives a `str`".

`Iterable[int]` means "anything you can loop over that gives ints": a list, a tuple, a set, a generator. A good rule: **accept the most general type** (`Iterable`) and **return a specific one** (`list`).

## Annotating a whole function: a worked example

1. Look at what each parameter is.
2. Look at what the function returns.
3. Write the hints. Do not change the body.

```python
# before
def total_length(words, sep):
    return sum(len(w) for w in words) + len(sep)

# after
def total_length(words: Iterable[str], sep: str) -> int:
    return sum(len(w) for w in words) + len(sep)
```

A function that builds a dict of counts is `-> dict[str, int]`. A function that returns a pair is `-> tuple[str, int]`. A function that may return nothing is `-> str | None`.

## Generics: "any type, used the same way"

A **generic** works for any type, and keeps track of which one. The letter `T` stands for "some type".

```python
def first[T](items: list[T]) -> T:
    return items[0]

print(first([1, 2]))      # -> 1       a checker knows: int
print(first(["a"]))       # -> a       a checker knows: str
```

If you pass `list[str]`, `T` is `str`, so the result is `str`. This `def first[T]` form needs Python 3.12 or newer.

A generic **class** works the same way. Here is a small box:

```python
class Box[T]:
    def __init__(self, item: T) -> None:
        self.item = item

    def get(self) -> T:
        return self.item

b = Box(5)
print(b.get())    # -> 5     a checker knows: int
```

A box can also be built by a **classmethod** (lesson 19). A classmethod that gives back an object of its own class is annotated with the class name in quotes, because the class is not finished yet when the line is read:

```python
class Bag[T]:
    def __init__(self) -> None:
        self._items: list[T] = []

    def add(self, item: T) -> None:
        self._items.append(item)

    def __len__(self) -> int:
        return len(self._items)

    @classmethod
    def from_items(cls, items: Iterable[T]) -> "Bag[T]":
        bag = cls()
        for item in items:
            bag.add(item)
        return bag

print(len(Bag.from_items([1, 2, 3])))    # -> 3
```

Older code writes generics with `TypeVar` and `Generic`:

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class Page(Generic[T]):
    def __init__(self, items: list[T], total: int) -> None:
        self.items = items
        self.total = total
```

You will use this idea for pages of an API: `Page[TaskRead]`.

## `Literal`: only these exact values

`Literal` limits a value to a few constants:

```python
from typing import Literal

Status = Literal["todo", "doing", "done"]

def show(status: Status) -> str:
    return f"status is {status}"
```

A checker rejects `show("blocked")`. (At runtime, Python still allows it. Hints are not checked.)

To get the allowed values as a tuple, use `typing.get_args`. Then you do not repeat the strings:

```python
from typing import get_args

ORDER = get_args(Status)
print(ORDER)                    # -> ('todo', 'doing', 'done')
print("done" in ORDER)          # -> True
print("blocked" in ORDER)       # -> False
```

## `TypedDict`: the shape of a dict

A `TypedDict` says which keys a dict has and the type of each value:

```python
from typing import TypedDict

class TaskDict(TypedDict):
    id: int
    title: str
    status: Status

task: TaskDict = {"id": 1, "title": "write", "status": "todo"}
```

At runtime it is a normal dict. The hints help your editor and checker.

### Checking data yourself

Hints do not check anything at runtime, so data from outside (like JSON) must be checked by hand, or by Pydantic (next lesson). A hand-made check uses `isinstance`. Remember from lesson 2 that `bool` is a kind of `int`, so `True` passes `isinstance(True, int)`. If a bool must not count as an int, rule it out:

```python
def valid_id(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)

print(valid_id(5))        # -> True
print(valid_id(True))     # -> False
print(valid_id("5"))      # -> False
```

A function that checks and then raises `ValueError` for any problem follows the same plan: check each field, one at a time, and raise a clear message.

## A type alias

A name for a type that you use again and again. In Python 3.12 and newer, use `type`:

```python
type UserId = int
type Scores = dict[str, list[float]]
```

## `Protocol`: "anything with these methods"

A `Protocol` describes the methods an object must have. No inheritance is needed (lesson 20).

```python
from typing import Protocol

class Notifier(Protocol):
    def send(self, to: str, message: str) -> None: ...

def alert(n: Notifier) -> None:
    n.send("ops", "disk full")     # any object with a matching send() works
```

## `Annotated`: a type plus extra information

`Annotated[T, extra]` is still `T` for a type checker. But a framework can read the `extra` part. This is how FastAPI attaches rules to parameters:

```python
from typing import Annotated
from fastapi import Query

def list_tasks(limit: Annotated[int, Query(ge=1, le=100)] = 20):
    ...
```

FastAPI sees: `limit` is an `int` (from the type), and it must be from 1 to 100 (from `Query(...)`).

## A little deeper (optional)

**Running a type checker.** It is a tool that reads your hints and reports mismatches, without running the program:

```bash
uv add --dev mypy
uv run mypy app/
```

Add it to your CI so a type error fails the build. Start gently and get stricter over time.

**Quotes around a type name.** `"Bag[T]"` in quotes is a **forward reference**: a name that is not ready yet at that line. Python reads it later.

## Common mistakes

- Writing `def f(x: int = None)`. The hint lies. Write `int | None = None`.
- Using `Any` too much. It switches checking off without a sound.
- Believing hints are checked at runtime. Only Pydantic and FastAPI do that.
- Forgetting that `True` passes `isinstance(True, int)`.
- Annotating a function that returns a list as `Iterator` (or the other way round).

## Interview corner

- **Q: Are type hints enforced?** No. They are information. Type checkers check them before running, and Pydantic and FastAPI read them while running to check data.
- **Q: What is the difference between `Any` and `object`?** `Any` switches checking off. `object` accepts everything, but you must check the type before using the value.
- **Q: How does FastAPI use type hints?** It reads the function signature to find where each parameter comes from, to convert and check input, and to build the API docs.
- **Q: What is a generic? Give an example.** A type that takes another type, like `Page[TaskRead]` or `def first[T](items: list[T]) -> T`.

## Summary

- Hints use `name: type` and `-> type`. Use the built-in forms like `list[int]` and the union form `X | None`.
- `Callable[[args], result]`, `Iterable`: accept general types, return specific ones.
- Generics: `def f[T](...)` and `class Box[T]`, or `TypeVar` with `Generic`.
- `Literal` for fixed values (`get_args` reads them), `TypedDict` for dict shapes, `Protocol`, `type` aliases and `Annotated`.
- Hints are not checked at runtime. Use mypy or pyright in CI, and Pydantic for data from outside.
