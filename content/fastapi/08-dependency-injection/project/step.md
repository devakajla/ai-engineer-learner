# Step 8 — Wire TaskFlow with dependency injection

`app/api/routes/tasks.py` still builds its own `task_service` at import time. Replace that with dependencies, so tests (and later the database) can plug in different implementations.

### 1. `get_settings()` with `@lru_cache` — `app/core/config.py`

Replace the module-level `settings = Settings()` with:

```python
@lru_cache
def get_settings() -> Settings:
    return Settings()
```

Update every import of `settings` to call `get_settings()` (or inject it).

### 2. A dependencies module — `app/api/deps.py`

```python
SettingsDep = Annotated[Settings, Depends(get_settings)]

_task_repository = InMemoryTaskRepository(seed=SEED)   # one store per process (for now)

def get_task_repository() -> InMemoryTaskRepository:
    return _task_repository

def get_task_service(repo: Annotated[InMemoryTaskRepository, Depends(get_task_repository)]) -> TaskService:
    return TaskService(repo)

TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]
```

### 3. Routes receive the service

Every task route takes `service: TaskServiceDep` and uses it. **Delete** the module-level `task_service` from `tasks.py`. `/health` takes `settings: SettingsDep`.

### 4. An application factory — `app/main.py`

```python
def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=settings.version, debug=settings.debug)
    app.include_router(health.router)
    app.include_router(tasks.router, prefix=settings.api_prefix)
    return app

app = create_app()
```

A factory lets tests and background workers build a fresh, fully configured app.

### Updated structure

```
app/
├── api/
│   ├── deps.py          ← new
│   └── routes/{health,tasks}.py
├── core/config.py       ← get_settings()
└── main.py              ← create_app()
```

### Checkpoint

The tests override `get_task_service` with a service over an **empty** repository and expect `/api/v1/tasks` to return `[]` — that only works if routes really use the dependency. They also check `get_settings` is cached, `create_app()` exists, and `tasks.py` no longer creates a service at import time.
