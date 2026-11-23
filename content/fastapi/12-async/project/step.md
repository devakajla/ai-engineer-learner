# Step 12 — Make TaskFlow async end to end

TaskFlow will soon call slow external services (LLMs, email, webhooks). Converting the data layer to **async SQLAlchemy** now means those waits never block the server. Every layer becomes `async`, top to bottom — mixing sync DB calls into async routes would block the event loop.

```bash
uv add aiosqlite
```

### 1. Async driver URL

- `Settings.database_url = "sqlite+aiosqlite:///./taskflow.db"` (update `.env.example`). In production this becomes `postgresql+asyncpg://...`.
- Alembic runs synchronously, so add a property:

```python
@property
def sync_database_url(self) -> str:
    return self.database_url.replace("+aiosqlite", "").replace("+asyncpg", "+psycopg")
```

and use `get_settings().sync_database_url` in `migrations/env.py`.

### 2. `app/db/session.py`

```python
engine = create_async_engine(get_settings().database_url)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)

async def get_db() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session
```

`DbSession` in `deps.py` becomes `Annotated[AsyncSession, Depends(get_db)]`.

### 3. Repository, Protocol and service

Every method becomes `async def` and every DB call is awaited: `await self.session.scalars(...)`, `await self.session.get(...)`, `await self.session.commit()`, `await self.session.refresh(...)`, `await self.session.delete(...)`. Update the `TaskRepository` Protocol and make all `TaskService` methods `async` too.

### 4. Routes

All task routes and `/health` become `async def` and `await` the service.

### 5. Verify

```bash
uv run alembic upgrade head
uv run fastapi dev app/main.py --port 8001
```

Everything in `/docs` must work exactly as before — that's a refactor, no behaviour change.

### Checkpoint

The tests check that the URL uses `aiosqlite`, that `get_db` is an async generator yielding an `AsyncSession`, that every task route, service method and repository method is a coroutine function, and run full CRUD through the API on a temporary async database.
