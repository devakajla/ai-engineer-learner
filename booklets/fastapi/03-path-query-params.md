# 3. Path and query parameters

A URL carries data. In `GET /tasks/5?done=true`, the `5` is a **path parameter** and `done=true` is a **query parameter**. FastAPI reads both and checks their types for you.

## Idea: which one to use?

| Use | When | Example |
| --- | --- | --- |
| **Path parameter** | it names *one specific thing* | `/tasks/5` |
| **Query parameter** | it filters, sorts or pages a *list* | `/tasks?done=true&limit=10` |

FastAPI decides by looking at your function:

- the name is inside `{}` in the path, so it is a **path** parameter.
- any other simple argument is a **query** parameter.

## Steps

We need some data to play with. For now it lives in a Python list. (Chapter 8 moves it to a real database.)

::: {.step}
Step 1: add fake data and a list route
:::

Open `app/main.py` and make it look like this:

```python
from fastapi import FastAPI

app = FastAPI(title="TaskFlow")

tasks = [
    {"id": 1, "title": "Learn FastAPI", "done": False},
    {"id": 2, "title": "Build TaskFlow", "done": True},
]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def list_tasks():
    return tasks
```

Save, then:

```bash
curl localhost:8000/tasks
# -> [{"id":1,"title":"Learn FastAPI","done":false},{"id":2,"title":"Build TaskFlow","done":true}]
```

::: {.step}
Step 2: a path parameter for one task
:::

```python
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return {"error": "not found"}
```

`{task_id}` in the path matches the argument `task_id`. The type hint `: int` does two jobs: FastAPI **converts** the text `"1"` to the number `1`, and it **rejects** anything that is not a number.

```bash
curl localhost:8000/tasks/1
# -> {"id":1,"title":"Learn FastAPI","done":false}
curl localhost:8000/tasks/abc
# -> {"detail":[{"type":"int_parsing","loc":["path","task_id"],"msg":"Input should be a valid integer, unable to parse string as an integer","input":"abc"}]}
```

You wrote no checking code, and still got a clear error with status `422`. The `loc` field says exactly where the problem is: `["path", "task_id"]`.

> Our `not found` answer above returns status `200`, which is wrong. We fix it properly in chapter 5.

::: {.step}
Step 3: query parameters for filtering
:::

```python
@app.get("/tasks")
def list_tasks(done: bool | None = None, limit: int = 20):
    items = [t for t in tasks if done is None or t["done"] == done]
    return items[:limit]
```

- `done: bool | None = None` means "optional; if not sent, it is `None`".
- `limit: int = 20` means "optional; if not sent, use 20".
- Anything **with a default** is optional. Anything **without a default** is required.

```bash
curl "localhost:8000/tasks?done=true"
# -> [{"id":2,"title":"Build TaskFlow","done":true}]
curl "localhost:8000/tasks?limit=1"
# -> [{"id":1,"title":"Learn FastAPI","done":false}]
```

Put the URL in quotes, because the shell treats `?` and `&` as special.

`bool` is clever: `true`, `1`, `yes` and `on` all work as true.

::: {.step}
Step 4: rules for the values with `Query` and `Path`
:::

A limit of `-5` or `1000000` makes no sense. Add rules:

```python
from typing import Annotated

from fastapi import FastAPI, Path, Query


@app.get("/tasks")
def list_tasks(
    done: bool | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    items = [t for t in tasks if done is None or t["done"] == done]
    return items[:limit]


@app.get("/tasks/{task_id}")
def get_task(task_id: Annotated[int, Path(ge=1)]):
    ...
```

`ge` means "greater than or equal", `le` means "less than or equal". Others: `gt`, `lt`, `min_length`, `max_length`, `pattern`.

```bash
curl "localhost:8000/tasks?limit=0"
# -> {"detail":[{"type":"greater_than_equal","loc":["query","limit"],"msg":"Input should be greater than or equal to 1","input":"0","ctx":{"ge":1}}]}
```

`Annotated[type, rule]` is the modern way to attach rules to a type. You will see it everywhere in FastAPI code.

## Order of routes matters

FastAPI checks routes **from top to bottom**. If you have `/tasks/{task_id}` and also `/tasks/summary`, put the **fixed** one first. Otherwise `summary` is read as a `task_id` and fails with `422`.

```python
@app.get("/tasks/summary")     # first: the fixed path
def summary(): ...

@app.get("/tasks/{task_id}")   # then: the pattern
def get_task(task_id: int): ...
```

## Enums: only these values

When a value must be one of a few choices, use an `Enum`.

```python
from enum import Enum

class SortBy(str, Enum):
    id = "id"
    title = "title"

@app.get("/tasks")
def list_tasks(sort: SortBy = SortBy.id):
    ...
```

`/tasks?sort=title` works, and `/tasks?sort=banana` returns `422`. The docs page even shows a dropdown.

::: {.box .checkpoint}
**Folder now** (unchanged; only `main.py` grew)

```
taskflow/
└── app/
    └── main.py     # /health, /tasks (with done and limit), /tasks/{task_id}
```

**Checkpoint:** run these and compare.

```bash
curl "localhost:8000/tasks?done=true"      # -> one task (id 2)
curl localhost:8000/tasks/abc              # -> 422 with "int_parsing"
curl "localhost:8000/tasks?limit=0"        # -> 422 with "greater_than_equal"
```
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Putting the pattern route (`/tasks/{task_id}`) above a fixed route (`/tasks/summary`).
- Forgetting quotes around a URL with `&` in curl, so the shell cuts it.
- Using a mutable default such as `tags: list = []`. For lists in queries use `Query()`.
- Returning a list of everything with no `limit`. Always cap list endpoints.
- Using a path parameter for a filter, like `/tasks/done`. Filters belong in the query string.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: Path vs query parameter?**
Path parameters identify one resource (`/tasks/5`). Query parameters filter, sort or page a collection (`?done=true`).

**Q: How does FastAPI know a function argument is a query parameter?**
If its name is not in the path, and it is a simple type (not a Pydantic model), it is a query parameter.

**Q: What happens on a wrong type?**
FastAPI returns `422 Unprocessable Entity` with details of where and why.

**Q: How do you make a query parameter required?**
Give it no default value.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Add an optional query parameter `q: str | None = None` to `GET /tasks` that keeps only tasks whose title contains `q` (ignore upper/lower case). Test `?q=fast`.
2. Add `offset: int = 0` and make `GET /tasks?limit=1&offset=1` return the second task. Add `ge=0` to `offset`.
3. Add `GET /tasks/summary` that returns `{"total": 2, "done": 1}`. Put it above `/tasks/{task_id}`. Then move it below and see what happens.
4. Create an `Enum` called `Order` with `asc` and `desc`, and add `?order=desc` to the list route. Sort by `id`.
5. **Think:** why is `GET /tasks?done=true` better than `GET /tasks/done/true`?
:::
