# 4. Request bodies and Pydantic

So far the client sent data in the URL. To **create** something, the client sends a **body**: a block of JSON.

```
POST /tasks
Content-Type: application/json

{"title": "Write the booklet"}
```

FastAPI uses **Pydantic** to read the body, check it, and give your function a clean Python object. If the data is wrong, your function never runs.

## Idea: a model describes the shape

A Pydantic **model** is a class that lists the fields you expect and their types.

```python
from pydantic import BaseModel

class TaskCreate(BaseModel):
    title: str
```

Copy this shape for now. Classes are explained fully in the Python booklet. All you need to know: `title: str` means "a field called `title` that must be text".

## Steps

::: {.step}
Step 1: a POST route with a model
:::

Add this to `app/main.py`:

```python
from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str


@app.post("/tasks", status_code=201)
def create_task(data: TaskCreate):
    task = {"id": len(tasks) + 1, "title": data.title, "done": False}
    tasks.append(task)
    return task
```

`data: TaskCreate` is a model, so FastAPI reads it from the **body**. Inside the function, `data.title` is a real, checked string.

```bash
curl -X POST localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Write booklet"}'
# -> {"id":3,"title":"Write booklet","done":false}
```

`-X POST` sets the method, `-H` adds a header and `-d` is the body. Or use `/docs`: it builds a form for you.

Try wrong data:

```bash
curl -X POST localhost:8000/tasks -H "Content-Type: application/json" -d '{}'
# -> {"detail":[{"type":"missing","loc":["body","title"],"msg":"Field required","input":{}}]}
```

::: {.step}
Step 2: add rules with `Field`
:::

```python
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    priority: int = Field(default=1, ge=1, le=5)
    tags: list[str] = []
```

- `Field(min_length=1, max_length=100)`: text length limits.
- `priority` has a default, so it is optional. `ge` and `le` limit it between 1 and 5.
- `tags: list[str] = []` is an optional list of texts. (Pydantic safely copies the default for each object, so the mutable-default trap from plain Python does not apply here.)

```bash
curl -X POST localhost:8000/tasks -H "Content-Type: application/json" -d '{"title": "x", "priority": 9}'
# -> {"detail":[{"type":"less_than_equal","loc":["body","priority"],"msg":"Input should be less than or equal to 5","input":9,"ctx":{"le":5}}]}
```

::: {.step}
Step 3: your own rule with a validator
:::

Sometimes built-in rules are not enough. Strip spaces and refuse a title that is only spaces:

```python
from pydantic import BaseModel, Field, field_validator


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    priority: int = Field(default=1, ge=1, le=5)
    tags: list[str] = []

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("title cannot be only spaces")
        return value
```

```bash
curl -X POST localhost:8000/tasks -H "Content-Type: application/json" -d '{"title": "  Buy milk  "}'
# -> the title is saved as "Buy milk"
curl -X POST localhost:8000/tasks -H "Content-Type: application/json" -d '{"title": "   "}'
# -> {"detail":[{"type":"value_error","loc":["body","title"],"msg":"Value error, title cannot be only spaces", ...}]}
```

A validator can **clean** the value (return a new one) or **reject** it (raise `ValueError`). `@classmethod` is required by Pydantic. Copy the shape.

::: {.step}
Step 4: a model for updates (PATCH)
:::

To change a task, the client sends only the fields that changed. Every field is optional:

```python
class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    done: bool | None = None
```

How do you tell "the client did not send `done`" from "the client sent `done: false`"? Use `model_dump(exclude_unset=True)`. It returns **only the fields the client actually sent**.

```python
@app.patch("/tasks/{task_id}")
def update_task(task_id: int, data: TaskUpdate):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if task is None:
        return {"error": "not found"}
    task.update(data.model_dump(exclude_unset=True))
    return task
```

```bash
curl -X PATCH localhost:8000/tasks/1 -H "Content-Type: application/json" -d '{"done": true}'
# -> {"id":1,"title":"Learn FastAPI","done":true}
```

Only `done` changed. The title stayed.

| Method | Meaning | Body |
| --- | --- | --- |
| `PUT` | replace the whole thing | all fields |
| `PATCH` | change a few fields | only the changed ones |

## Why separate models for create and update?

`TaskCreate` says what a client may send when **creating**. `TaskUpdate` says what a client may send when **changing**. Later you will add `TaskOut`, the shape you **send back**. Using one model for everything is a classic beginner mistake: a client could set fields it should never control (like `id` or `owner_id`).

## Nested models and unions

Models can contain other models:

```python
class Address(BaseModel):
    city: str
    pincode: str = Field(pattern=r"^\d{6}$")

class Profile(BaseModel):
    name: str
    address: Address
```

The client sends `{"name": "Asha", "address": {"city": "Pune", "pincode": "411001"}}` and every level is checked.

You can also mix a body with path and query parameters in one function:

```python
@app.put("/tasks/{task_id}")
def replace_task(task_id: int, data: TaskCreate, notify: bool = False): ...
```

`task_id` comes from the path, `data` from the body and `notify` from the query.

::: {.box .checkpoint}
**Folder now**

```
taskflow/
└── app/
    └── main.py     # + TaskCreate, TaskUpdate, POST /tasks, PATCH /tasks/{id}
```

**Checkpoint:**

```bash
curl -X POST localhost:8000/tasks -H "Content-Type: application/json" -d '{"title": "  Buy milk  "}'
# -> status 201, title is "Buy milk" (spaces removed)
curl -X POST localhost:8000/tasks -H "Content-Type: application/json" -d '{"title": ""}'
# -> status 422 with "string_too_short"
```
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Using one model for create, update and output.
- Forgetting the `Content-Type: application/json` header in curl. The body is then not read as JSON.
- Using `model_dump()` for a PATCH. It includes unset fields as `None` and overwrites real data. Use `exclude_unset=True`.
- Accepting `dict` as a body. You lose all the checking.
- Trusting the client with fields like `id`, `is_admin` or `owner_id`. Keep them out of input models.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: How does FastAPI know that an argument is the request body?**
When its type is a Pydantic model, it is read from the JSON body.

**Q: PUT vs PATCH in FastAPI?**
For PUT, require all fields. For PATCH, make all fields optional and apply only what was sent, using `model_dump(exclude_unset=True)`.

**Q: What happens when validation fails?**
FastAPI returns `422` with a list of errors. Your function is not called.

**Q: Pydantic validators: when would you use one?**
For rules that built-in `Field` options cannot express, such as cleaning text or checking two fields together (`model_validator`).
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Add `due_in_days: int | None` to `TaskCreate`, between 1 and 365, optional.
2. Write a validator that lowercases every tag in `tags` and removes duplicates.
3. Send a `POST` with the wrong JSON type for `tags` (a string, not a list). Read the error. Which field name does `loc` show?
4. Add `DELETE /tasks/{task_id}` that removes a task from the list and returns status `204`.
5. **Think:** why should the `id` field not be part of `TaskCreate`?
:::
