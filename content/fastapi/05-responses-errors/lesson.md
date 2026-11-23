---
title: Responses, status codes & errors
summary: Control what your API sends back (shape, status code, errors) and build a full create / read / update / delete API.
plan_ids: [FA-01, BE-01]
---

So far, your routes return any dict you build. Real APIs are stricter. Every response has a **declared shape** and the **right status code**, and errors look the same everywhere.

This lesson finishes **CRUD** for TaskFlow. CRUD means the four basic jobs of most APIs: **C**reate, **R**ead, **U**pdate, **D**elete.

## `response_model`: say what you send back

Imagine your code stores a user with a secret password hash. You do not want to send the hash to the client by accident.

With `response_model` you give FastAPI a model that describes the **output**:

```python
from pydantic import BaseModel

class UserIn(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str

@app.post("/users", response_model=UserOut)
def create_user(payload: UserIn):
    user = {"id": 1, "email": payload.email, "password_hash": "x9f..."}
    return user
```

The function returns a dict with `password_hash`, but the client receives only this:

```json
{"id": 1, "email": "a@b.c"}
```

`response_model` does three jobs:

1. **Filters.** Only the fields in `UserOut` are sent. Secrets cannot leak by accident.
2. **Checks.** If your code returns the wrong shape, you get a clear error instead of silently bad data.
3. **Documents.** The response appears in `/docs`.

For a list, write `response_model=list[UserOut]`.

You can also use a return type hint: `def create_user(...) -> UserOut:`. Use `response_model=` when you return a plain dict (or a database object, later) and want the model applied.

## Status codes

By default, FastAPI answers `200`. To use another code, set `status_code` on the decorator:

```python
from fastapi import status

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task():
    return {"id": 1}

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    return None   # 204 means: no body
```

`status.HTTP_201_CREATED` is just the number `201` with a readable name. Use these names instead of bare numbers, so your code explains itself.

| Operation | Success code |
|---|---|
| read (GET) | 200 |
| create (POST) | **201** |
| update (PUT / PATCH) | 200, with the updated thing in the body |
| delete (DELETE) | **204**, no body |

## Errors with `HTTPException`

To stop and send an error, **raise** an `HTTPException`:

```python
from fastapi import HTTPException, status

TASKS = {1: {"id": 1, "title": "Learn FastAPI"}}

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = TASKS.get(task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task
```

```text
GET /tasks/1   -> 200 {"id": 1, "title": "Learn FastAPI"}
GET /tasks/99  -> 404 {"detail": "Task not found"}
```

Why **raise** and not **return**?

- Raising stops the function at once, even if you are deep inside a helper function.
- FastAPI turns it into a response with your status code and `{"detail": ...}`.
- If you `return` an error dict instead, the status code is still `200`, and the client thinks it worked.

Which code for which problem:

| Situation | Code |
|---|---|
| the thing does not exist | 404 |
| a duplicate (email already used) | 409 Conflict |
| invalid values | 422 (FastAPI does this for you) |
| not logged in, or a bad token | 401 |
| logged in, but not allowed | 403 |

## Do not repeat yourself: a helper that raises

Three routes (read, update, delete) all need "find the task, or send 404". Write it once as a small helper function:

```python
def get_task_or_404(task_id: int):
    task = TASKS.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
```

Now each route calls `task = get_task_or_404(task_id)`. If the task is missing, the helper raises and the route stops.

You can also name a type once and reuse it:

```python
from typing import Annotated
from fastapi import Path

TaskId = Annotated[int, Path(ge=1)]

@app.get("/tasks/{task_id}")
def get_task(task_id: TaskId):
    return get_task_or_404(task_id)
```

## PUT vs PATCH in code

`PUT` replaces the whole thing. The client sends every field.

`PATCH` changes **only the fields the client sent**. This needs care. Look at this model, where every field is optional:

```python
class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None
```

When the client sends `{"done": true}`, the model still has a `title` field, with the value `None`. How do you know that the client **did not send** the title, and did not mean "set the title to nothing"?

Use `model_dump(exclude_unset=True)`. It returns only the fields that the client really sent:

```python
update = TaskUpdate(done=True)
print(update.model_dump())                    # -> {'title': None, 'done': True}
print(update.model_dump(exclude_unset=True))  # -> {'done': True}
```

Use it in a PATCH route:

```python
@app.patch("/tasks/{task_id}")
def update_task(task_id: int, payload: TaskUpdate):
    task = get_task_or_404(task_id)
    changes = payload.model_dump(exclude_unset=True)
    task.update(changes)        # dict.update changes only the keys in `changes`
    return task
```

- `PATCH {"done": true}` changes only `done`. The title stays.
- `PATCH {"description": null}` clears the description, because the client **sent** it as `null` on purpose.
- `PATCH {}` changes nothing.

Without `exclude_unset=True`, every missing field would be written as `None` and you would erase data. It is the most important line of a PATCH route.

## Worked example: hide a secret, and return 404

Exercise 1 asks you to hide a secret field with `response_model`, and to send `404` for a missing thing. Here is the same pattern for a different problem: **products** with a secret cost price.

```python
PRODUCTS = {
    1: {"id": 1, "name": "Pen", "price": 10, "cost_price": 4},
}
```

Goal:

```text
GET /products/1   -> 200 {"id": 1, "name": "Pen", "price": 10}
GET /products/9   -> 404 {"detail": "Product not found"}
```

**Step 1.** Write the output model. It lists only the fields the client may see.

```python
class ProductOut(BaseModel):
    id: int
    name: str
    price: int
```

**Step 2.** Write the route. Put the model in `response_model`.

```python
@app.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int):
    product = PRODUCTS.get(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
```

Notice: you return the full dict with `cost_price`. You do **not** delete it by hand. `response_model` removes it.

**Step 3.** Test both lines of the goal.

```python
client = TestClient(app)
print(client.get("/products/1").json())        # -> {'id': 1, 'name': 'Pen', 'price': 10}
print(client.get("/products/9").status_code)   # -> 404
```

## Backend concept: errors are part of your contract

Clients write code that depends on your errors, too. Good APIs:

- Use the **correct status codes**. Client code has `if` statements that depend on them.
- Return errors in **one shape** everywhere. FastAPI's shape is `{"detail": ...}`.
- Never leak internal details in an error (stack traces, SQL, file paths). Attackers can use them.
- Write **useful messages**: `"Task not found"`, not `"Error"`.

## A little deeper (optional)

- **Idempotency again.** `PUT` and `DELETE` are safe to retry. `PATCH {"done": true}` is also safe to retry, because it sets a value. `PATCH {"add": 1}` is not. Prefer "set this value" over "change by this much".
- **Building a model from an object.** `TaskRead.model_validate(some_dict)` makes a model from a dict. Later, with a database, you will read from objects. For that you add `model_config = ConfigDict(from_attributes=True)`.
- A `Location` header (for example `Location: /tasks/42`) is often sent with a `201` to say where the new thing lives.

## Common mistakes

- Sending a body with `204`. A `204` must be empty.
- Returning `None` with status `200` when the thing is not found. Use `404`.
- Forgetting `exclude_unset=True` in PATCH, which erases data.
- Using one model for input and output, so internal fields leak.
- Returning an error dict instead of raising `HTTPException`.

## Interview corner

- **Q: How do you stop a password hash from appearing in a response?** Use a separate output model, `response_model=UserOut`, that does not have the field.
- **Q: What is the pitfall when you build PATCH?** Telling "not sent" apart from "sent as null". Use `model_dump(exclude_unset=True)`.
- **Q: Which status code (and header) fits creating a resource?** `201 Created`, usually with a `Location: /tasks/{id}` header.

## Summary

- `response_model` filters, checks and documents what you return.
- Use `201` for create, `204` (empty) for delete, `200` for read and update.
- `raise HTTPException(status_code=..., detail=...)` sends an error. Pick the code with care.
- Write "find or 404" once, in a helper function.
- PATCH = a model with optional fields + `model_dump(exclude_unset=True)`.
