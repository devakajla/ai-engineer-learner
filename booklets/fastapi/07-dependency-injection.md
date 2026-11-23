# 7. Dependency injection

In chapter 6, our route file creates its own service: `service = TaskService(TaskRepository())`. This is a **hidden dependency**: the routes are glued to one specific repository, and you cannot swap it, for example for a test.

**Dependency injection (DI)** fixes that. The idea: *a function declares what it needs, and the framework supplies it.*

Real life: a chef does not grow vegetables. He says "I need onions" and the kitchen supplies them. He does not care where they come from.

## Idea: `Depends`

```python
from fastapi import Depends

def get_greeting() -> str:
    return "hello"

@app.get("/hi")
def hi(greeting: str = Depends(get_greeting)):
    return {"message": greeting}
```

When a request arrives, FastAPI calls `get_greeting()` first, then passes the result as `greeting`. The route never calls `get_greeting` itself.

## Steps

::: {.step}
Step 1: make a place for shared dependencies
:::

Create `app/api/deps.py`. This file holds all the "supplier" functions of the API layer.

```python
from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.repositories.task_repo import TaskRepository
from app.services.task_service import TaskService


@lru_cache
def get_task_repo() -> TaskRepository:
    return TaskRepository()


def get_task_service(
    repo: Annotated[TaskRepository, Depends(get_task_repo)],
) -> TaskService:
    return TaskService(repo)


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]
```

Read it from the bottom up:

- A route asks for a `TaskService`.
- To make one, FastAPI calls `get_task_service`.
- That function asks for a `TaskRepository`, so FastAPI calls `get_task_repo` first.

Dependencies can need other dependencies. FastAPI builds the whole chain for you. `@lru_cache` makes sure there is **one** repository (our fake data lives in it), not a new empty one per request.

`TaskServiceDep` is a **shortcut name**. Writing `Annotated[TaskService, Depends(get_task_service)]` in every route is long. Now a route just says `service: TaskServiceDep`.

::: {.step}
Step 2: use it in the routes
:::

Edit `app/api/routes/tasks.py`. Delete the old global `service = ...` line and its imports, then change the routes:

```python
from typing import Annotated

from fastapi import APIRouter, Query, Response, status

from app.api.deps import TaskServiceDep
from app.schemas.task import TaskCreate, TaskOut, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskOut])
def list_tasks(
    service: TaskServiceDep,
    done: bool | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    return service.list_tasks(done, limit, offset)


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate, service: TaskServiceDep):
    return service.create_task(data)


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, service: TaskServiceDep):
    return service.get_task(task_id)


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, data: TaskUpdate, service: TaskServiceDep):
    return service.update_task(task_id, data)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, service: TaskServiceDep):
    service.delete_task(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
```

The routes **no longer know** which repository is used. Nothing changed for the client. Run the checkpoint from chapter 6 again to prove it.

::: {.step}
Step 3: a dependency for pagination
:::

`limit` and `offset` will repeat in many list routes. Put them in one **class** dependency in `deps.py`:

```python
from typing import Annotated

from fastapi import Depends, Query


class Pagination:
    def __init__(
        self,
        limit: Annotated[int, Query(ge=1, le=100)] = 20,
        offset: Annotated[int, Query(ge=0)] = 0,
    ):
        self.limit = limit
        self.offset = offset


PaginationDep = Annotated[Pagination, Depends()]
```

`Depends()` with nothing inside means "use the class itself". FastAPI reads the `__init__` arguments as query parameters. Use it:

```python
@router.get("", response_model=list[TaskOut])
def list_tasks(service: TaskServiceDep, page: PaginationDep, done: bool | None = None):
    return service.list_tasks(done, page.limit, page.offset)
```

Now every list endpoint gets the same rules for free.

::: {.step}
Step 4: a dependency that checks something
:::

A dependency can also **guard** a route. For example, an admin-only key sent in a header. Add to `deps.py`:

```python
from fastapi import Header, HTTPException

from app.core.config import Settings, get_settings


def require_admin_key(
    settings: Annotated[Settings, Depends(get_settings)],
    x_admin_key: Annotated[str | None, Header()] = None,
) -> None:
    if x_admin_key != settings.admin_key:
        raise HTTPException(status_code=403, detail="Admin key required")
```

(Add `admin_key: str = "dev-admin-key"` to `Settings`.) Use it without needing its value:

```python
@router.delete("/{task_id}", dependencies=[Depends(require_admin_key)])
```

`dependencies=[...]` runs the guard **before** the function. You can also put it on a whole router: `APIRouter(dependencies=[Depends(require_admin_key)])`. Notice that `get_settings` is injected too. **Settings are just another dependency.**

::: {.step}
Step 5: dependencies with `yield` (setup and cleanup)
:::

Some things must be opened and closed: a database session, a file, a connection. A dependency with `yield` runs the code **before** `yield` to set up, hands over the value, and runs the code **after** `yield` for cleanup, even if an error happened.

```python
def get_resource():
    resource = open_something()      # setup
    try:
        yield resource               # the route runs here
    finally:
        resource.close()             # cleanup, always runs
```

Chapter 8 uses this exact pattern for the database session.

## The superpower: swapping dependencies in tests

Because the route asks for `get_task_service` instead of building one, a test can replace it:

```python
from app.main import app
from app.api.deps import get_task_repo
from app.repositories.task_repo import TaskRepository

class EmptyRepo(TaskRepository):
    def __init__(self):
        self._tasks = []

app.dependency_overrides[get_task_repo] = lambda: EmptyRepo()
```

Now `GET /api/v1/tasks` returns `[]`, without touching any real data. `app.dependency_overrides` is a dictionary: "when someone asks for X, give them Y". Chapter 15 uses it for all tests. This is why DI exists.

::: {.box .checkpoint}
**Folder now**

```
app/
├── api/
│   ├── deps.py          # NEW: get_task_repo, get_task_service, Pagination
│   ├── router.py
│   └── routes/ health.py, tasks.py   # tasks.py now uses TaskServiceDep
├── core/ schemas/ repositories/ services/
└── main.py
```

**Checkpoint:** all earlier `curl` commands behave exactly the same. Then `curl "localhost:8000/api/v1/tasks?limit=1&offset=1"` returns only the second task.
:::

::: {.box .why}
**Why `deps.py` and not inside each route file?**

Dependencies are shared by many routes (`CurrentUser`, `SessionDep`). One file means one place to look, and no circular imports between route files.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Calling the dependency yourself: `Depends(get_service())` with brackets. Pass the **function**, not its result.
- Creating a new heavy object (like a repository with data) on each request instead of caching it.
- Using global variables instead of dependencies, which makes testing hard.
- Hiding business rules inside a dependency. Dependencies supply and guard. Rules live in services.
- Forgetting `Annotated`, and writing the old default-value style everywhere. Both work, but `Annotated` is cleaner.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: What is dependency injection and why use it?**
A function declares what it needs and the framework provides it. It removes hidden globals, lets you share logic, and lets tests replace parts.

**Q: How do you replace a dependency in a test?**
`app.dependency_overrides[original] = replacement`.

**Q: What does `yield` do in a dependency?**
Code before `yield` is setup, the yielded value is given to the route, and code after `yield` is cleanup. It always runs.

**Q: `Depends` in the argument list vs `dependencies=[...]`?**
The first gives you the returned value. The second only runs the dependency, for example a check, without passing a value.

**Q: Can dependencies depend on other dependencies?**
Yes. FastAPI builds the whole chain.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Write a dependency `get_request_id` that reads an optional `X-Request-ID` header, or makes a random id, and returns it. Use it in one route and return the id in the JSON.
2. Add a class `Pagination` field `max_limit` from settings instead of a fixed `100`.
3. Use `dependencies=[Depends(require_admin_key)]` on the whole `tasks` router. Test with and without the header `X-Admin-Key: dev-admin-key`.
4. In a scratch test, override `get_task_repo` with a repository that has 5 tasks. Check that the list route returns 5.
5. **Think:** why is `service = TaskService(TaskRepository())` at the top of a route file harder to test than `Depends`?
:::
