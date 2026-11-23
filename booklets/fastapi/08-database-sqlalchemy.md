# 8. A real database: SQLAlchemy and Alembic

Our tasks live in a Python list. Restart the server and they vanish. Time for a real database.

You will meet three tools:

| Tool | Job |
| --- | --- |
| **SQLAlchemy** | lets Python code talk to a database (an ORM, "object relational mapper") |
| **Async driver** (`aiosqlite`, later `asyncpg`) | the low-level connection that does not block |
| **Alembic** | **migrations**: safe, versioned changes to your tables |

If SQL is new, read chapters 3 and 4 of the Backend booklet first. Here we focus on wiring it into FastAPI.

## Idea: classes are tables

With an ORM, a Python class describes a table, and each object is one row.

```python
class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
```

`Mapped[int]` is the Python type, and `mapped_column(...)` adds database details (primary key, length, index).

Why SQLite now? It is a database in a single file, with nothing to install. We write code that works the same on Postgres later. Only the connection URL changes.

## Steps

::: {.step}
Step 1: install the packages
:::

```bash
uv add "sqlalchemy[asyncio]" aiosqlite alembic
```

The `[asyncio]` part matters. It installs `greenlet`, which SQLAlchemy's async mode needs.

::: {.step}
Step 2: the database folder
:::

```bash
mkdir app/db app/models
touch app/db/__init__.py app/models/__init__.py
```

Add the database address to `Settings` (`app/core/config.py`):

```python
database_url: str = "sqlite+aiosqlite:///./taskflow.db"
```

Read the URL: `dialect+driver://where`. For SQLite it is a file path. For Postgres later: `postgresql+asyncpg://user:password@localhost:5432/taskflow`.

`app/db/base.py`: one base class that all tables inherit from:

```python
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
```

`app/db/session.py`: the **engine** (the connection pool) and the **session** (one conversation with the database):

```python
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

engine = create_async_engine(get_settings().database_url)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session
```

- The **engine** is created once. It owns a pool of connections.
- A **session** is created **per request**. It tracks the objects you load and change, and sends the changes on `commit()`.
- `get_session` is a **dependency with `yield`** (chapter 7). The session opens, the route uses it, and it closes after, even on errors.
- `expire_on_commit=False` keeps objects usable after `commit()`. Without it, async code often fails when it touches an object after commit.

::: {.step}
Step 3: the models (tables)
:::

`app/models/user.py`:

```python
from datetime import UTC, datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
```

`app/models/task.py`:

```python
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    done: Mapped[bool] = mapped_column(default=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
```

Decisions worth noticing (you learned the reasons in the Backend booklet):

- Every table has a primary key `id`.
- `email` is `unique` (the database blocks duplicates) and `index`ed (fast lookup).
- `owner_id` is a **foreign key** to `users.id`, with an index, because we will always filter by owner.
- We store a **hash** of the password, never the password.

Make `app/models/__init__.py` list them, so importing `app.models` registers every table:

```python
from app.models.task import Task
from app.models.user import User

__all__ = ["Task", "User"]
```

::: {.step}
Step 4: migrations with Alembic
:::

Do **not** create tables with code at startup. In a real project, the structure of the database changes over time, and every environment (your laptop, a teammate, production) must change the same way. A **migration** is a small Python file that says "to go from version A to B, do this". Alembic keeps the list.

```bash
uv run alembic init -t async alembic
```

This creates `alembic.ini` and an `alembic/` folder. The `-t async` template is for async engines.

Open `alembic/env.py`. Find the line `target_metadata = None` and replace it with:

```python
from app.core.config import get_settings
from app.db.base import Base
import app.models  # noqa: F401  (so every table is registered on Base.metadata)

config.set_main_option("sqlalchemy.url", get_settings().database_url)
target_metadata = Base.metadata
```

You told Alembic two things: where the database is (from our settings, so there is one source of truth) and what the tables should look like (our models). Now it can compare the two.

Generate the first migration:

```bash
uv run alembic revision --autogenerate -m "create users and tasks"
# -> Detected added table 'users'
# -> Detected added index 'ix_users_email' on '('email',)'
# -> Detected added table 'tasks'
# -> Detected added index 'ix_tasks_owner_id' on '('owner_id',)'
# -> Generating alembic/versions/97510e61c71d_create_users_and_tasks.py ... done
```

Your file name has a different random id. **Open it and read it.** Autogenerate is a helper, not magic. It contains `upgrade()` with `op.create_table(...)` and `downgrade()` that undoes it. Apply it:

```bash
uv run alembic upgrade head
# -> Running upgrade  -> 97510e61c71d, create users and tasks
uv run alembic current
# -> 97510e61c71d (head)
```

A file `taskflow.db` now exists, with `users`, `tasks` and an `alembic_version` table (which remembers the current version).

The migration loop you will repeat forever:

@@ flow | Figure 8.1: how a schema change travels.
Edit the model|add a column|blue -> revision --autogenerate|Alembic writes the file;you read it|yellow -> upgrade head|the database changes|green
@@ end

::: {.step}
Step 5: the repository talks to the database
:::

Rewrite `app/repositories/task_repo.py`. The *job* is the same (list, get, add, delete), but now it is real and `async`:

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self, owner_id: int, done: bool | None, limit: int, offset: int) -> list[Task]:
        stmt = (
            select(Task).where(Task.owner_id == owner_id).order_by(Task.id).limit(limit).offset(offset)
        )
        if done is not None:
            stmt = stmt.where(Task.done == done)
        result = await self.session.scalars(stmt)
        return list(result)

    async def get(self, task_id: int) -> Task | None:
        return await self.session.get(Task, task_id)

    async def add(self, task: Task) -> Task:
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def save(self, task: Task) -> Task:
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def delete(self, task: Task) -> None:
        await self.session.delete(task)
        await self.session.commit()
```

Reading the pieces:

- `select(Task).where(...)` builds a query. It reads like SQL. `await session.scalars(stmt)` runs it.
- `session.get(Task, id)` finds one row by primary key.
- `session.add(obj)` + `await session.commit()` saves a new row. `refresh` reloads it, so `id` and `created_at` are filled in.
- Every call that talks to the database uses `await`.

Notice that the **service and routes barely change**. This is the payoff of the layers from chapter 6.

::: {.step}
Step 6: update the service, schema and dependencies
:::

`app/schemas/task.py`: `TaskOut` must read from an ORM object, and now has `created_at`:

```python
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    done: bool
    created_at: datetime
```

`from_attributes=True` lets Pydantic read `task.title` (attributes) and not only `task["title"]` (dict keys).

`app/services/task_service.py`: methods become `async`, and every task now belongs to an **owner**:

```python
from app.core.exceptions import TaskNotFound
from app.models.task import Task
from app.repositories.task_repo import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    def __init__(self, repo: TaskRepository):
        self.repo = repo

    async def list_tasks(self, owner_id: int, done: bool | None, limit: int, offset: int) -> list[Task]:
        return await self.repo.list(owner_id, done, limit, offset)

    async def create_task(self, owner_id: int, data: TaskCreate) -> Task:
        return await self.repo.add(Task(title=data.title, owner_id=owner_id))

    async def get_task(self, owner_id: int, task_id: int) -> Task:
        task = await self.repo.get(task_id)
        # Same error for "missing" and "not yours": we do not reveal other users' ids.
        if task is None or task.owner_id != owner_id:
            raise TaskNotFound(task_id)
        return task

    async def update_task(self, owner_id: int, task_id: int, data: TaskUpdate) -> Task:
        task = await self.get_task(owner_id, task_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(task, field, value)
        return await self.repo.save(task)

    async def delete_task(self, owner_id: int, task_id: int) -> None:
        task = await self.get_task(owner_id, task_id)
        await self.repo.delete(task)
```

The ownership check lives in **one** method (`get_task`) and is reused by update and delete. This prevents the "IDOR" bug from the Backend booklet: a user cannot touch another user's task.

`app/api/deps.py`: replace the in-memory parts. We don't have login yet, so a **temporary** dependency pretends user `1` is logged in:

```python
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.repositories.task_repo import TaskRepository
from app.services.task_service import TaskService

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_task_service(session: SessionDep) -> TaskService:
    return TaskService(TaskRepository(session))


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]


def get_current_user_id() -> int:
    """TEMPORARY: pretend user 1 is always logged in. Chapter 11 makes this real."""
    return 1


CurrentUserId = Annotated[int, Depends(get_current_user_id)]


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

(We removed the in-memory `get_task_repo` and the admin-key guard from chapter 7. The admin key was just practice.)

Update `app/api/routes/tasks.py`: routes become `async` and pass the owner id.

```python
from fastapi import APIRouter, Response, status

from app.api.deps import CurrentUserId, PaginationDep, TaskServiceDep
from app.schemas.task import TaskCreate, TaskOut, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskOut])
async def list_tasks(
    owner_id: CurrentUserId, service: TaskServiceDep, page: PaginationDep, done: bool | None = None
):
    return await service.list_tasks(owner_id, done, page.limit, page.offset)


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(data: TaskCreate, owner_id: CurrentUserId, service: TaskServiceDep):
    return await service.create_task(owner_id, data)


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(task_id: int, owner_id: CurrentUserId, service: TaskServiceDep):
    return await service.get_task(owner_id, task_id)


@router.patch("/{task_id}", response_model=TaskOut)
async def update_task(task_id: int, data: TaskUpdate, owner_id: CurrentUserId, service: TaskServiceDep):
    return await service.update_task(owner_id, task_id, data)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, owner_id: CurrentUserId, service: TaskServiceDep):
    await service.delete_task(owner_id, task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
```

Run the server and try:

```bash
curl -X POST localhost:8000/api/v1/tasks -H "Content-Type: application/json" -d '{"title": "Saved in a real database"}'
# -> {"id":1,"title":"Saved in a real database","done":false,"created_at":"2026-11-22T09:15:01.123456Z"}
```

Now **stop the server, start it again**, and call `curl localhost:8000/api/v1/tasks`. The task is still there. It lives in `taskflow.db`.

> SQLite does not check foreign keys unless you turn it on. So `owner_id=1` works even though no user 1 exists yet. A real Postgres database **would** refuse it. Chapter 11 creates real users, and this stops being a shortcut.

## Moving to Postgres later

Change only the URL (and install the driver: `uv add asyncpg`):

```
DATABASE_URL=postgresql+asyncpg://taskflow:taskflow@localhost:5432/taskflow
```

The models, the repository and the migrations stay the same. Chapter 16 runs Postgres in Docker. This portability is why we separated the layers.

::: {.box .checkpoint}
**Folder now**

```
taskflow/
├── alembic.ini
├── alembic/
│   ├── env.py
│   └── versions/97510e61c71d_create_users_and_tasks.py
├── taskflow.db                 # created by the migration (git-ignored)
└── app/
    ├── db/       base.py, session.py          # NEW
    ├── models/   user.py, task.py             # NEW
    ├── repositories/ task_repo.py             # now uses the database
    ├── services/ task_service.py              # async, owner-aware
    ├── schemas/  task.py                      # TaskOut has created_at
    └── api/      deps.py, routes/tasks.py     # SessionDep, CurrentUserId
```

**Checkpoint:** create a task, restart the server, list tasks. The task must still be there. `uv run alembic current` shows `(head)`.
:::

## Changing the schema later: a second migration

Say you want a `due_date` on tasks. The loop from Figure 8.1:

1. Add `due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)` to `Task`.
2. `uv run alembic revision --autogenerate -m "add due date"`
3. Read the new file. It has `op.add_column("tasks", ...)`.
4. `uv run alembic upgrade head`.

Existing rows get `NULL`. That is why a new column on a table with data should be **nullable** or have a default.

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Forgetting `await`. You get a `coroutine` object instead of data, plus a warning.
- Creating the engine or session inside every function. Create the engine once; create a session per request.
- Editing the database by hand instead of writing a migration. Then no other environment matches.
- Never reading the autogenerated migration. It can miss renames (it sees a drop plus an add and loses data).
- Using `expire_on_commit=True` (the default) with async code, then crashing on attribute access.
- Using SQLAlchemy models as the response. Always convert through a schema (`TaskOut`).
- Calling `Base.metadata.create_all()` in production instead of migrations.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: What is an ORM and what are its trade-offs?**
It maps classes to tables so you write Python instead of SQL. It is productive and safe from injection, but it can hide slow queries (like N+1), so you must still know SQL.

**Q: Engine vs session?**
The engine owns the connection pool and is created once. A session is a short unit of work, created per request.

**Q: Why migrations?**
They version the schema, so every environment changes in the same, repeatable, reversible way.

**Q: Why `from_attributes=True`?**
It lets a Pydantic model read from an ORM object's attributes instead of a dict.

**Q: How do you avoid N+1 in SQLAlchemy?**
Load related rows with `selectinload` or `joinedload` instead of touching a relationship in a loop.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Add `due_date` to `Task` and run the whole migration loop. Then look at the new file in `alembic/versions/`.
2. Add `GET /api/v1/tasks/count` returning `{"count": n}` for the current owner, using `select(func.count())` in the repository. Where does each piece of code go?
3. Run `uv run alembic downgrade -1` and then `upgrade head`. What changed in `taskflow.db` each time?
4. Add `priority: int` to `Task` with `default=1`. Why must a new column on a table with rows have a default or be nullable?
5. **Think:** why does the service raise `TaskNotFound` for a task that belongs to someone else, instead of a `403`?
:::
