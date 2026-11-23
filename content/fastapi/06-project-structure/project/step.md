# Step 6 — Restructure TaskFlow like a production codebase

Time to refactor. **The API's behaviour stays the same** (except it moves to `/api/v1`). What changes is *where code lives*. This is exactly what you'd do on a real team once a service grows past a couple of files.

### Target structure

```
taskflow/
├── app/
│   ├── __init__.py
│   ├── main.py                     # create app + include routers (≈15 lines)
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py               # Settings + settings = Settings()
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── health.py           # router for /health
│   │       └── tasks.py            # router for /tasks (HTTP only)
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── task.py                 # unchanged
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_service.py         # TaskService + TaskNotFoundError
│   └── repositories/
│       ├── __init__.py
│       └── task_repository.py      # InMemoryTaskRepository + SEED data
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

### 1. Config — `app/core/config.py`

```bash
uv add pydantic-settings
```

`Settings(BaseSettings)` with `app_name="TaskFlow"`, `version="0.1.0"`, `debug=False`, `api_prefix="/api/v1"`, reading `.env` (`SettingsConfigDict(env_file=".env", extra="ignore")`). Create a module-level `settings = Settings()`.

Add `.env.example` documenting `APP_NAME`, `DEBUG`, `API_PREFIX`. Check `.env` is in `.gitignore`.

### 2. Repository — `app/repositories/task_repository.py`

`InMemoryTaskRepository` owns the storage. Methods: `list()`, `get(id)`, `add(data)`, `update(id, changes)`, `delete(id) -> bool`. Move the 3 seed tasks here (e.g. a `SEED` list passed to the constructor). **No filtering, no HTTP, no validation** — storage only.

### 3. Service — `app/services/task_service.py`

`TaskService(repo)` with `list(done, priority, limit)`, `get`, `create`, `update`, `delete`. Filtering and "not found" decisions live here. Missing tasks raise **`TaskNotFoundError`** — never `HTTPException`.

### 4. Routes — `app/api/routes/`

- `health.py`: `router = APIRouter(tags=["health"])`, `GET /health` → `{"status": "ok", "app": settings.app_name}`.
- `tasks.py`: `router = APIRouter(prefix="/tasks", tags=["tasks"])`. Routes call the service and translate `TaskNotFoundError` → 404. For now create one shared `task_service = TaskService(InMemoryTaskRepository(seed=SEED))` in this module (lesson 8 replaces it with dependency injection).

### 5. `app/main.py` — wiring only

```python
app = FastAPI(title=settings.app_name, version=settings.version, debug=settings.debug)
app.include_router(health.router)
app.include_router(tasks.router, prefix=settings.api_prefix)
```

Health stays at `/health` (load balancers expect a fixed path); the API moves to **`/api/v1/tasks`**.

### 6. Verify, then commit

Open `/docs`: two groups (health, tasks), every task route under `/api/v1`. Then:

```bash
git add -A && git commit -m "Refactor into routes/services/repositories with settings"
```

### Checkpoint

The tests check the folder structure, that settings load from env vars, that tasks live under `/api/v1/tasks` (old `/tasks` → 404), that the service works without HTTP and raises `TaskNotFoundError`, and that `main.py` stays thin. Claude then reviews your layering.
