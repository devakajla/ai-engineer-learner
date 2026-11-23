# Step 9 — Persist tasks in SQLite (raw SQL)

Time to stop losing data on restart. You'll write a **repository backed by SQLite using plain `sqlite3`** — real SQL, parameterized queries, an index. Because of the layering from step 6 and DI from step 8, **routes and services barely change**. That's the payoff of good structure.

### 1. A repository contract — `app/repositories/base.py`

```python
class TaskRepository(Protocol):
    def list(self, done: bool | None = None, priority: str | None = None, limit: int = 20) -> list[Task]: ...
    def get(self, task_id: int) -> Task | None: ...
    def add(self, data: Task) -> Task: ...
    def update(self, task_id: int, changes: Task) -> Task | None: ...
    def delete(self, task_id: int) -> bool: ...
```

Filtering now belongs to the repository (the **database** filters, not Python). Update `InMemoryTaskRepository.list` to accept the same arguments, and make `TaskService.list` delegate to `repo.list(...)`. Type the service against `TaskRepository`.

### 2. `SqliteTaskRepository` — `app/repositories/sqlite_task_repository.py`

- `SqliteTaskRepository(db_path)` creates the schema if missing (`CREATE TABLE IF NOT EXISTS`):

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY,
    title       TEXT    NOT NULL,
    description TEXT,
    priority    TEXT    NOT NULL DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
    done        INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS ix_tasks_done ON tasks (done);
```

- Open a **short-lived connection per operation** (`sqlite3.connect(path)` + `with conn:` for commit/rollback, then close).
- Return plain dicts with `done` converted back to `bool`.
- **Every value goes through `?` placeholders.** Column names in UPDATE may be built dynamically only from a fixed whitelist.

### 3. Config and wiring

- `Settings.database_path: str = "taskflow.db"` (+ `DATABASE_PATH` in `.env.example`).
- `get_task_repository(settings: SettingsDep)` returns `SqliteTaskRepository(settings.database_path)`.
- Add `*.db` to `.gitignore` — never commit database files.

### 4. Try it

```bash
uv run fastapi dev app/main.py --port 8001
# create a few tasks in /docs, stop the server, start it again: they're still there
sqlite3 taskflow.db "SELECT * FROM tasks;"
```

### Checkpoint

The tests use a temporary database file: CRUD and filters through the repository and through the API (via `dependency_overrides`), persistence across repository instances, an SQL-injection title stored safely, the `ix_tasks_done` index, the `CHECK` constraint, and that `.gitignore` ignores `*.db`.
