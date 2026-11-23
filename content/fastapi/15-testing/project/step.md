# Step 15 — TaskFlow's own test suite

Until now *this app* checked your project. A real project carries **its own tests**, so every change (and every future step) is verified in seconds. Build a suite that would catch real bugs.

```bash
uv add --dev pytest httpx
```

In `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
```

### Target structure

```
tests/
├── __init__.py
├── conftest.py            # fixtures: isolated DB, client, make_task factory
├── test_health.py
├── test_tasks.py          # API integration tests
└── test_task_service.py   # unit tests with a fake repository
```

### 1. `tests/conftest.py`

- `session_factory` fixture: a **new temp SQLite file per test** (`tmp_path`), `create_async_engine(..., poolclass=NullPool)`, create the schema with `Base.metadata.create_all` (fine in tests), dispose at the end.
- `client` fixture: `app = create_app()`, override `get_db` with a session from that factory via `app.dependency_overrides`, yield `TestClient(app)`, clear overrides.
- A **factory fixture** `make_task(**fields)` that creates a task through the API and returns its JSON — keeps tests short.

Your tests must **never** use the real `taskflow.db`.

### 2. What your suite must cover

At minimum (the checkpoint will inject bugs into each of these and expects your suite to fail):

- **create**: 201, returned fields — including that the **priority you send comes back**; defaults; validation 422s
- **get**: one task; 404 body
- **patch**: changes the sent fields (assert the new values!), keeps the others; 404
- **delete**: 204, then GET is 404
- **list**: envelope + paging, **`done` and `priority` filters**, search, sort, bad sort → 422
- a few **unit tests** of `TaskService` with a fake repository (no DB, no HTTP)

Aim for **at least 10 test functions**. Use `@pytest.mark.parametrize` for validation cases.

### 3. Run it

```bash
uv run pytest -q
```

### Checkpoint

The checker runs **your** suite (it must pass, with ≥ 10 tests, without creating the dev database), then runs it four more times against TaskFlow with injected bugs — create ignoring the priority, update doing nothing, delete doing nothing, the `done` filter ignored — and expects your suite to fail every time.
