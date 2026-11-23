# 5. Responses, status codes and errors

Until now our code returned whatever it liked, even `{"error": "not found"}` with status `200`. That is a lie: the request failed but the status says "OK". In this chapter we fix it. We make the **shape of answers** and the **errors** honest and consistent.

## Idea: three things to control

1. **The data** you send back: what fields? (`response_model`)
2. **The status code**: did it work? (`status_code`)
3. **The errors**: what do you say when it fails? (`HTTPException` and handlers)

## Steps

::: {.step}
Step 1: a model for output
:::

Add a model for the shape of a task going **out**:

```python
class TaskOut(BaseModel):
    id: int
    title: str
    done: bool
```

Use it on the routes with `response_model`:

```python
@app.get("/tasks", response_model=list[TaskOut])
def list_tasks(...): ...

@app.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(...): ...

@app.post("/tasks", response_model=TaskOut, status_code=201)
def create_task(...): ...
```

What does `response_model` do?

- It **filters** the answer. Extra fields in your return value are dropped.
- It **checks** your answer. If you forget a field, FastAPI returns `500` instead of sending bad data.
- It **writes the docs** for the response.

The filtering is a security tool. A quick proof:

```python
class UserIn(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str

@app.post("/users", response_model=UserOut, status_code=201)
def create_user(data: UserIn):
    return {"id": 1, "email": data.email, "password": data.password}
```

```bash
curl -X POST localhost:8000/users -H "Content-Type: application/json" \
  -d '{"email": "a@x.com", "password": "secret"}'
# -> {"id":1,"email":"a@x.com"}      <- the password is not in the answer
```

We returned the password by mistake, but `response_model=UserOut` removed it. **Always use a separate output model for anything with secrets.**

::: {.step}
Step 2: honest status codes
:::

| Situation | Code | How in FastAPI |
| --- | --- | --- |
| Created something | `201` | `status_code=201` |
| Deleted, nothing to return | `204` | `status_code=204` |
| Not found | `404` | `raise HTTPException(404)` |
| Wrong input | `422` | automatic |
| Duplicate | `409` | `raise HTTPException(409)` |

Use the named constants to avoid magic numbers:

```python
from fastapi import status

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
```

::: {.step}
Step 3: raise errors with `HTTPException`
:::

```python
from fastapi import HTTPException

@app.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")
```

`raise` stops the function at once. FastAPI turns the exception into an HTTP response:

```bash
curl -i localhost:8000/tasks/99
# -> HTTP/1.1 404 Not Found
# -> {"detail":"Task not found"}
```

The same for delete, which must return `204` and **no body**:

```python
from fastapi import Response

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            return Response(status_code=204)
    raise HTTPException(status_code=404, detail="Task not found")
```

::: {.step}
Step 4: your own error type
:::

Soon our rules will live in a service layer (chapter 6) that must **not** know about HTTP. So the service raises its **own** error, and one handler in the API layer turns it into a `404`. Practise the idea now.

Create `app/exceptions.py`:

```python
class TaskNotFound(Exception):
    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f"Task {task_id} not found")
```

In `main.py`, add a handler:

```python
from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions import TaskNotFound


@app.exception_handler(TaskNotFound)
async def task_not_found_handler(request: Request, exc: TaskNotFound):
    return JSONResponse(
        status_code=404,
        content={"error": "not_found", "message": str(exc)},
    )
```

Now any code anywhere can `raise TaskNotFound(5)`, and the client sees:

```bash
curl -i localhost:8000/tasks/99
# -> HTTP/1.1 404 Not Found
# -> {"error":"not_found","message":"Task 99 not found"}
```

This is the **error-translation pattern**: your rules raise meaningful errors, and one place decides how they look in HTTP. Every API should have a consistent error shape, so clients can handle them with one piece of code.

## Documenting other responses

Tell the docs about errors your route can return:

```python
@app.get(
    "/tasks/{task_id}",
    response_model=TaskOut,
    responses={404: {"description": "Task not found"}},
)
```

## Other response types

| Class | Use |
| --- | --- |
| `JSONResponse` | JSON with a custom status or headers |
| `Response` | nothing, or raw bytes (`204`) |
| `RedirectResponse` | send the client elsewhere (`307`) |
| `FileResponse` | send a file |
| `StreamingResponse` | send data in pieces (chapter 13) |

::: {.box .checkpoint}
**Folder now**

```
taskflow/
└── app/
    ├── __init__.py
    ├── main.py          # routes, models, exception handler
    └── exceptions.py    # our own error types (new)
```

**Checkpoint:**

```bash
curl -i localhost:8000/tasks/99      # -> 404 and {"error":"not_found","message":"Task 99 not found"}
curl -i -X DELETE localhost:8000/tasks/1   # -> 204 with an empty body
```
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Returning `{"error": ...}` with status `200`.
- Returning a database object with a secret field and no `response_model`.
- Raising `HTTPException` deep inside business code. Raise your own error, translate it at the edge.
- Sending a body with `204`. It must be empty.
- Using different error shapes in different routes.
- Using `response_model` with a type the data does not match, and getting a `500`.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: What does `response_model` do?**
It filters and validates the data you return and documents the response. It stops secret fields from leaking.

**Q: `raise HTTPException` vs `return JSONResponse`?**
`raise` stops the function at once, from any depth. `return` only works at the end of your route.

**Q: How do you keep error responses consistent?**
Define your own exception classes and register handlers that produce one error format.

**Q: 404 or 403 when a user asks for another user's task?**
Often `404`, so you do not reveal that the task exists.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Make `PATCH /tasks/{id}` raise `TaskNotFound` when the id is missing.
2. Add a `DuplicateTitle` error and return `409` with the same error shape when a task with the same title already exists.
3. Add a `UserOut` that hides the `password` field and test it in `/docs`.
4. Use `responses={...}` so `/docs` shows a `404` example for `get_task`.
5. **Think:** why is it better for a service to raise `TaskNotFound` than `HTTPException(404)`?
:::
