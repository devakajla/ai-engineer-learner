# 6. Project structure and settings

Our `main.py` now holds models, routes, data, and an error handler. It is about 100 lines and already crowded. This chapter is the most important one in the booklet. You will **refactor** it into a clean structure, one small move at a time, and you will learn *how to decide where each piece goes*. After this, you can structure any project.

## Idea: one job per file

Look at what is mixed together in `main.py` right now:

| Piece in `main.py` | What it is | Its proper home |
| --- | --- | --- |
| `TaskCreate`, `TaskUpdate`, `TaskOut` | shapes of data | `schemas/` |
| the `tasks` list and the code that searches it | data access | `repositories/` |
| "raise `TaskNotFound` if missing" | a rule | `services/` |
| `@app.get(...)` functions | HTTP | `api/routes/` |
| `TaskNotFound` class | an error type | `core/` |
| the `FastAPI(...)` line and handler | building the app | `main.py` |

Use the **five questions** from chapter 1 each time.

## The target

```
taskflow/
├── pyproject.toml
├── .env
└── app/
    ├── __init__.py
    ├── main.py                  # creates the app
    ├── core/
    │   ├── config.py            # settings
    │   └── exceptions.py        # our error types
    ├── schemas/
    │   └── task.py              # TaskCreate, TaskUpdate, TaskOut
    ├── repositories/
    │   └── task_repo.py         # in-memory data (a database in chapter 8)
    ├── services/
    │   └── task_service.py      # the rules
    └── api/
        ├── router.py            # joins all routes under /api/v1
        └── routes/
            ├── health.py
            └── tasks.py
```

## Steps

Work in this order. After **each step**, save and check that `/docs` still loads. Small steps mean small bugs.

::: {.step}
Step 1: create the folders
:::

```bash
mkdir -p app/core app/schemas app/repositories app/services app/api/routes
touch app/core/__init__.py app/schemas/__init__.py app/repositories/__init__.py \
      app/services/__init__.py app/api/__init__.py app/api/routes/__init__.py
```

::: {.step}
Step 2: move the error type to `core/`
:::

Move `app/exceptions.py` to `app/core/exceptions.py` (`git mv app/exceptions.py app/core/exceptions.py`). Its content stays the same:

```python
class TaskNotFound(Exception):
    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f"Task {task_id} not found")
```

::: {.step}
Step 3: move the models to `schemas/`
:::

Create `app/schemas/task.py`. This holds **only shapes of data**:

```python
from pydantic import BaseModel, Field, field_validator


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("title cannot be only spaces")
        return value


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    done: bool | None = None


class TaskOut(BaseModel):
    id: int
    title: str
    done: bool
```

::: {.step}
Step 4: the repository: the only code that touches data
:::

Create `app/repositories/task_repo.py`:

```python
class TaskRepository:
    """Keeps tasks in a Python list. Chapter 8 swaps this for a real database."""

    def __init__(self):
        self._tasks: list[dict] = [
            {"id": 1, "title": "Learn FastAPI", "done": False},
            {"id": 2, "title": "Build TaskFlow", "done": True},
        ]

    def list(self, done: bool | None, limit: int, offset: int) -> list[dict]:
        items = [t for t in self._tasks if done is None or t["done"] == done]
        return items[offset : offset + limit]

    def get(self, task_id: int) -> dict | None:
        return next((t for t in self._tasks if t["id"] == task_id), None)

    def add(self, title: str) -> dict:
        task = {"id": len(self._tasks) + 1, "title": title, "done": False}
        self._tasks.append(task)
        return task

    def delete(self, task: dict) -> None:
        self._tasks.remove(task)
```

Notice what is **not** here: no `HTTPException`, no status codes, no rules. It only stores and finds. A repository that only does "get, add, delete" is easy to replace later.

::: {.step}
Step 5: the service: the rules
:::

Create `app/services/task_service.py`:

```python
from app.core.exceptions import TaskNotFound
from app.repositories.task_repo import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    def __init__(self, repo: TaskRepository):
        self.repo = repo

    def list_tasks(self, done: bool | None, limit: int, offset: int) -> list[dict]:
        return self.repo.list(done, limit, offset)

    def get_task(self, task_id: int) -> dict:
        task = self.repo.get(task_id)
        if task is None:
            raise TaskNotFound(task_id)
        return task

    def create_task(self, data: TaskCreate) -> dict:
        return self.repo.add(data.title)

    def update_task(self, task_id: int, data: TaskUpdate) -> dict:
        task = self.get_task(task_id)
        task.update(data.model_dump(exclude_unset=True))
        return task

    def delete_task(self, task_id: int) -> None:
        self.repo.delete(self.get_task(task_id))
```

The rule "a missing task is an error" lives here, in **one** place. Update and delete reuse `get_task`, so you never forget the check. Again: no `HTTPException`. The service does not know that HTTP exists.

::: {.step}
Step 6: routes with an `APIRouter`
:::

An `APIRouter` is a mini app. Each file of routes makes one, and `main.py` plugs them in.

`app/api/routes/health.py`:

```python
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    return {"status": "ok"}
```

`app/api/routes/tasks.py`:

```python
from typing import Annotated

from fastapi import APIRouter, Query, Response, status

from app.repositories.task_repo import TaskRepository
from app.schemas.task import TaskCreate, TaskOut, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])

# One shared service for now. Chapter 7 replaces this with dependency injection.
service = TaskService(TaskRepository())


@router.get("", response_model=list[TaskOut])
def list_tasks(
    done: bool | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    return service.list_tasks(done, limit, offset)


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate):
    return service.create_task(data)


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int):
    return service.get_task(task_id)


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, data: TaskUpdate):
    return service.update_task(task_id, data)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    service.delete_task(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
```

Look how **thin** the routes are. Each one reads the request, calls the service, and returns. No rules, no data access. That is what a healthy route looks like: usually 1 to 3 lines.

`prefix="/tasks"` means every path in this file starts with `/tasks`. `tags` groups the routes in `/docs`.

`app/api/router.py` joins everything under a version prefix:

```python
from fastapi import APIRouter

from app.api.routes import tasks

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(tasks.router)
```

Now the URLs are `/api/v1/tasks`. The `v1` lets you ship `v2` later without breaking existing clients (chapter 2 of the Backend booklet).

::: {.step}
Step 7: settings that come from the environment
:::

Hard-coded values (database URL, secret keys) must not live in code. Different machines need different values, and secrets must never reach git. The answer: **environment variables**, read by `pydantic-settings`.

```bash
uv add pydantic-settings
```

`app/core/config.py`:

```python
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TaskFlow"
    debug: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

Settings are fields with types and defaults. Pydantic reads each from an environment variable of the same name (`APP_NAME`, `DEBUG`), or from the `.env` file. A wrong type fails **at startup**, not at 3 am in production.

`@lru_cache` makes `get_settings()` build the object only once and reuse it.

Create a `.env` file (it is already in `.gitignore`):

```
APP_NAME=TaskFlow (dev)
DEBUG=true
```

Also create `.env.example` with the same names but fake values, and commit **that** one. A teammate copies it to `.env` and fills in real values.

::: {.step}
Step 8: `main.py` becomes tiny
:::

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.api.routes import health
from app.core.config import get_settings
from app.core.exceptions import TaskNotFound


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, debug=settings.debug)

    @app.exception_handler(TaskNotFound)
    async def task_not_found_handler(request: Request, exc: TaskNotFound):
        return JSONResponse(
            status_code=404,
            content={"error": "not_found", "message": str(exc)},
        )

    app.include_router(health.router)
    app.include_router(api_router)
    return app


app = create_app()
```

`create_app()` is called an **application factory**. It builds the app in one function, which makes it easy to build a second copy with different settings (useful in tests).

`main.py` now has one job: **assemble the pieces**. It holds no business logic.

::: {.box .checkpoint}
**Folder now**

```
taskflow/
├── .env
├── .env.example
├── pyproject.toml
└── app/
    ├── main.py
    ├── core/         config.py, exceptions.py
    ├── schemas/      task.py
    ├── repositories/ task_repo.py
    ├── services/     task_service.py
    └── api/
        ├── router.py
        └── routes/   health.py, tasks.py
```

**Checkpoint:** the URLs moved under `/api/v1`. Run:

```bash
curl localhost:8000/health
# -> {"status":"ok"}
curl localhost:8000/api/v1/tasks
# -> [{"id":1,"title":"Learn FastAPI","done":false},{"id":2,"title":"Build TaskFlow","done":true}]
curl -i localhost:8000/api/v1/tasks/99
# -> HTTP/1.1 404 Not Found   {"error":"not_found","message":"Task 99 not found"}
curl -X POST localhost:8000/api/v1/tasks -H "Content-Type: application/json" -d '{"title": "  Buy milk "}'
# -> {"id":3,"title":"Buy milk","done":false}
```

The behaviour is **exactly the same as before**. That is the point of a refactor: the structure changed, nothing else did.
:::

## Why this structure? The payoff

| Change you will make later | Files you touch |
| --- | --- |
| Use a real database | `repositories/` only (chapter 8) |
| Add "max 50 tasks per user" | `services/` only |
| Rename a JSON field | `schemas/` only |
| Add login | a new `routes/auth.py` and a dependency |
| Add `/api/v2` | `api/` only |

If one small change forces you to edit five files, your structure is wrong. If it touches one file, it is right.

## The import rule

Imports must point **downwards** only:

```
routes  ->  services  ->  repositories  ->  models
   \           \                               ^
    ->  schemas  ------------------------------/
   everyone may import from core
```

A repository must never import from `routes`. A service must never import `fastapi`. If you ever need to, the code is in the wrong layer. When two files import each other you get a **circular import** error. Following this one-way rule prevents it.

## When is a layered structure too much?

For a 30-line script, one file is perfect. Layers pay off when the project has more than a couple of routes, a database, and more than one person. Our TaskFlow will have all of that, so we start layered. A simple signal to split: **the file no longer fits on two screens**, or you scroll to find things.

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Putting SQL or `HTTPException` inside services.
- Putting business rules inside routes ("fat routes").
- A giant `utils.py` or `helpers.py` that everything imports. Name files by what they hold.
- Committing `.env` with real secrets.
- Importing `main.py` from other modules, which creates circular imports. Nothing should import `main`.
- Moving everything at once. Move one piece, run, and check.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: How do you structure a FastAPI project?**
By layers: routes (HTTP), services (rules), repositories (data), schemas (shapes), core (config and shared code), plus `main.py` to assemble. Each layer only talks to the one below.

**Q: What is an `APIRouter`?**
A mini application that groups related routes with a shared prefix and tags. `main.py` includes it.

**Q: Why use `pydantic-settings`?**
It reads configuration from environment variables with type checking, so secrets stay out of code and wrong settings fail at startup.

**Q: What is an application factory?**
A function (`create_app`) that builds and returns the app, so you can create differently configured copies, for example in tests.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Sort these into a folder: (a) `class UserOut(BaseModel)`, (b) `def hash_password(...)`, (c) "a user may not have more than 100 tasks", (d) `SELECT ... FROM tasks`, (e) `@router.get("/users/me")`.
2. Add `max_tasks: int = 100` to `Settings`, read it from `.env`, and make `TaskService.create_task` raise a new `TaskLimitReached` error when the limit is hit. Add a handler that returns `409`.
3. Draw (on paper) the arrows between your folders. Which arrow must never exist?
4. Create `app/api/routes/version.py` with `GET /version` returning the `app_name`, and include it. Which files did you touch?
5. **Think:** why is it a good sign that `routes/tasks.py` has no `if` statements about tasks?
:::
