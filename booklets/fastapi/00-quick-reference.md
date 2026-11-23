# Quick Reference

Open this page when you forget a name. Every item is explained in a chapter.

## Commands

| What | Command |
| --- | --- |
| Make a project | `mkdir taskflow && cd taskflow && uv init --bare` |
| Add a package | `uv add "fastapi[standard]"` |
| Add a dev-only package | `uv add --dev pytest` |
| Run the dev server | `uv run fastapi dev app/main.py` |
| Run for production | `uv run fastapi run app/main.py --workers 4` |
| Run tests | `uv run pytest -q` |
| New migration | `uv run alembic revision --autogenerate -m "add tasks"` |
| Apply migrations | `uv run alembic upgrade head` |
| Undo last migration | `uv run alembic downgrade -1` |
| Open the docs | `http://127.0.0.1:8000/docs` |

## Routes

```python
from fastapi import FastAPI, APIRouter, status

app = FastAPI(title="TaskFlow")
router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("")                                   # list
@router.get("/{task_id}")                         # one
@router.post("", status_code=status.HTTP_201_CREATED)   # create
@router.put("/{task_id}")                         # replace
@router.patch("/{task_id}")                       # change some fields
@router.delete("/{task_id}", status_code=204)     # remove

app.include_router(router, prefix="/api/v1")
```

## Where does each value come from?

| It looks like | FastAPI reads it from | Example |
| --- | --- | --- |
| a name inside `{}` in the path | **path** | `task_id: int` |
| a simple type not in the path | **query string** | `limit: int = 20` |
| a Pydantic model | **JSON body** | `data: TaskCreate` |
| `Header()` | a header | `x_token: Annotated[str, Header()]` |
| `Cookie()` | a cookie | `theme: Annotated[str, Cookie()]` |
| `Form()` | an HTML form field | `username: Annotated[str, Form()]` |
| `File()` / `UploadFile` | an uploaded file | `file: UploadFile` |
| `Depends(...)` | the return value of another function | `service: Annotated[S, Depends(get_s)]` |

## Validation helpers

```python
from typing import Annotated
from fastapi import Query, Path
from pydantic import BaseModel, Field

limit: Annotated[int, Query(ge=1, le=100)] = 20
task_id: Annotated[int, Path(ge=1)]

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    priority: int = Field(default=1, ge=1, le=5)
```

## Responses and errors

```python
from fastapi import HTTPException, Response
from fastapi.responses import JSONResponse, RedirectResponse, StreamingResponse

raise HTTPException(status_code=404, detail="Task not found")
return Response(status_code=204)
@app.get("/tasks", response_model=list[TaskOut])
```

## Dependency injection

```python
from typing import Annotated
from fastapi import Depends

SessionDep = Annotated[AsyncSession, Depends(get_session)]

async def route(session: SessionDep): ...
app.dependency_overrides[get_session] = fake_get_session   # in tests
```

## Status codes

`200` OK, `201` Created, `202` Accepted, `204` No Content, `400` Bad Request, `401` Not logged in, `403` Not allowed, `404` Not Found, `409` Conflict, `413` Too Large, `415` Wrong Type, `422` Validation error, `429` Too Many, `500` Server error.

## SQLAlchemy 2.0 async

```python
from sqlalchemy import select
row  = await session.get(Task, 5)                          # by primary key
rows = (await session.scalars(select(Task).where(Task.done))).all()
session.add(obj); await session.commit(); await session.refresh(obj)
await session.delete(obj); await session.commit()
```

## Settings

```python
class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./taskflow.db"
    model_config = SettingsConfigDict(env_file=".env")
```

## Folder map (what goes where)

| Folder | Holds | Knows about |
| --- | --- | --- |
| `app/api/routes/` | route functions (HTTP) | schemas, services |
| `app/schemas/` | Pydantic shapes for requests and responses | nothing else |
| `app/services/` | business rules | repositories, exceptions |
| `app/repositories/` | database queries | models, session |
| `app/models/` | SQLAlchemy tables | `Base` |
| `app/core/` | settings, security, logging, errors | nothing else |
| `app/db/` | engine, session, `Base` | settings |
| `tests/` | tests, mirrors the app | everything |
