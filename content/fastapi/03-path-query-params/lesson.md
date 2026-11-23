---
title: Path & query parameters
summary: Read data from the URL using type hints, and let FastAPI check it for you.
plan_ids: [FA-01]
---

In lesson 1 you learned: the **path** says which thing, the **query** gives options. Now you will see how to read both in FastAPI. The nice part: you only use **function parameters and type hints**. There is no parsing code.

## Path parameters

A **path parameter** is a part of the URL that changes, such as the id in `/tasks/42`. You write it in curly braces:

```python
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    return {"task_id": task_id}
```

- `{task_id}` in the path is matched by **name** to the function parameter `task_id`.
- The type hint `int` tells FastAPI two things. First, **convert** the text `"42"` into the number `42`. Second, **check** that it really is a number.

```text
GET /tasks/42   -> 200 {"task_id": 42}
GET /tasks/abc  -> 422 {"detail": [{"type": "int_parsing", "loc": ["path", "task_id"], ...}]}
```

You wrote no `if` at all, yet bad input is rejected with a clear error. `loc` tells the client exactly where the problem is (`path`, `task_id`). This is why FastAPI APIs are pleasant to use.

### Route order matters

FastAPI checks routes **from top to bottom** and uses the first one that matches. So a fixed path must come **before** a path with a parameter that could also match it.

```python
@app.get("/tasks/today")        # fixed path: first
def tasks_today():
    return {"which": "today"}

@app.get("/tasks/{task_id}")    # parameter path: after
def get_task(task_id: int):
    return {"task_id": task_id}
```

If you swap them, then `GET /tasks/today` matches `/tasks/{task_id}` first. Then `"today"` fails the `int` check and you get `422`.

### Fixed choices with `Enum`

Sometimes only a few values are allowed, for example `daily`, `weekly` or `monthly`. An **`Enum`** is a class that lists the allowed values.

```python
from enum import Enum

class Period(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"

print(Period.weekly.value)   # -> weekly
print(Period("daily"))       # -> Period.daily
```

Use it as a type hint and FastAPI accepts only those values:

```python
@app.get("/reports/{period}")
def report(period: Period):
    return {"period": period.value}
```

```text
GET /reports/weekly  -> 200 {"period": "weekly"}
GET /reports/yearly  -> 422
```

Two details:

- `class Period(str, Enum)` means each member is also a string. That makes it easy to compare with text and to send as JSON.
- `/docs` shows a drop-down list with the allowed values.

If you need a number for each member (like how many days), a normal `if` or a small dictionary does the job:

```python
SIZE = {Period.daily: 1, Period.weekly: 7}
print(SIZE[Period.weekly])   # -> 7
```

## Query parameters

A **query parameter** is an option after the `?` in the URL. In FastAPI, any function parameter that is **not** in the path is a query parameter:

```python
@app.get("/tasks")
def list_tasks(done: bool | None = None, limit: int = 20):
    return {"done": done, "limit": limit}
```

| Request | `done` | `limit` |
|---|---|---|
| `/tasks` | `None` | `20` |
| `/tasks?done=true&limit=5` | `True` | `5` |
| `/tasks?done=0` | `False` | `20` |
| `/tasks?limit=many` | (not used) | 422 error |

Rules to remember:

- A parameter **with a default value** is optional.
- A parameter **without a default** is required. If it is missing, the client gets `422`.
- `bool` accepts `true`/`false`, `1`/`0`, `yes`/`no` and `on`/`off`. Anything else (like `ok`) gives `422`.
- `bool | None = None` is the usual way to say "an optional filter". It means: a bool, or nothing.

### Rules for a value: `Query` and `Path`

You often need more than a type. For example: "the id must be at least 1", or "the search text must be 2 to 50 letters". Use `Query(...)` for query parameters and `Path(...)` for path parameters:

```python
from typing import Annotated
from fastapi import Path, Query

@app.get("/tasks/{task_id}")
def get_task(task_id: Annotated[int, Path(ge=1)]):
    return {"task_id": task_id}

@app.get("/search")
def search(
    q: Annotated[str, Query(min_length=2, max_length=50)],
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
):
    return {"q": q, "limit": limit}
```

How to read `Annotated[int, Path(ge=1)]`: "an `int`, with the extra rule `ge=1`". The type comes first, then the rules.

The rules you will use most:

| For | Rule | Meaning |
|---|---|---|
| numbers | `gt`, `ge`, `lt`, `le` | greater than, greater or equal, less than, less or equal |
| text | `min_length`, `max_length` | shortest and longest allowed |
| text | `pattern` | must match a pattern |

If a value breaks a rule, FastAPI answers `422`.

> **Always put an upper limit on `limit`.** Without it, one client can ask for `limit=10000000` and overload your database.

### Many values for one name

A client can repeat a name in the query: `/tasks?tag=work&tag=urgent`. To collect them in a list, use `Query()` on a list type:

```python
@app.get("/tasks")
def list_tasks(tag: Annotated[list[str] | None, Query()] = None):
    return {"tag": tag}
# /tasks?tag=work&tag=urgent  ->  {"tag": ["work", "urgent"]}
```

## Worked example: a fixed route and a parameter route

Exercise 1 combines three things: a fixed path, a path parameter, and a rule on the number. Here is the same pattern for a different problem: **books**.

Goal:

```text
GET /books/featured  -> {"book_id": "featured"}
GET /books/5         -> {"book_id": 5}
GET /books/0         -> 422      (id must be 1 or more)
GET /books/abc       -> 422
```

**Step 1.** Write the fixed route first, so it cannot be swallowed.

```python
@app.get("/books/featured")
def featured_book():
    return {"book_id": "featured"}
```

**Step 2.** Write the parameter route after it. Add `Path(ge=1)` for the rule.

```python
@app.get("/books/{book_id}")
def get_book(book_id: Annotated[int, Path(ge=1)]):
    return {"book_id": book_id}
```

**Step 3.** Test each line of the goal with `TestClient`.

```python
client = TestClient(app)
print(client.get("/books/featured").json())   # -> {'book_id': 'featured'}
print(client.get("/books/5").json())          # -> {'book_id': 5}
print(client.get("/books/0").status_code)     # -> 422
print(client.get("/books/abc").status_code)   # -> 422
```

If you put the two routes in the other order, the first line would fail with `422`. Route order is the main trap here.

## Backend concept: validate at the boundary

Your API is the **boundary** (the border) between the outside world and your code. People and programs outside can send anything: wrong types, huge numbers, empty text.

The rule in good backends: **check everything once, at the border. Then trust it inside.**

Type hints and rules like `ge=1` do this checking for you. Inside your function, `task_id` is guaranteed to be an `int` that is at least 1. You do not need `if` checks everywhere.

## A little deeper (optional)

- **400 vs 422.** FastAPI uses `422` when the request is well-formed but the values are invalid. Many APIs also use `400` for business rules, such as "the due date is in the past". Choose one habit and keep it everywhere.
- **Why `X | None = None`?** Writing `done: bool = None` is a lie: it says "bool" but allows `None`. Write `bool | None = None` so the hint tells the truth.
- Parameter names in the function must match the names in the URL. If you write `{task_id}` in the path, the parameter must be called `task_id`.

## Common mistakes

- No upper bound on `limit`, or on a page size.
- Putting `/tasks/{task_id}` above `/tasks/today`.
- Using plain `str` when only a few values are allowed. Use an `Enum`.
- Writing `done: bool = None` instead of `bool | None = None`.
- Forgetting that query values arrive as text, and that FastAPI converts them only if you add a type hint.

## Interview corner

- **Q: When do you use a path parameter and when a query parameter?** A path parameter names one specific thing (`/tasks/42`). A query parameter gives optional options such as filters, sorting and paging (`?done=true&limit=20`).
- **Q: Why does FastAPI return 422 and not 400?** `422` means the request is well-formed but its data is not valid. FastAPI's checking errors use it.
- **Q: Why limit the page size?** To protect the server and the database from huge responses. It is a simple defence against overload.

## Summary

- Path parameters come from `{name}` in the path. Every other function parameter is a query parameter.
- Type hints convert the value and check it. A bad value gives `422` with a precise `loc`.
- A default makes a parameter optional. No default means required.
- `Annotated[type, Path(...)]` and `Annotated[type, Query(...)]` add rules like `ge`, `le`, `min_length`. Always bound `limit`.
- Use an `Enum` for fixed choices. Put fixed routes before parameter routes.
