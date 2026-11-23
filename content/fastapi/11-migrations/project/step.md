# Step 11 — Manage the schema with Alembic (and add due dates)

`create_all` at startup can't evolve the schema. Replace it with migrations — and use them right away to add a feature: **task due dates**.

```bash
uv add alembic
uv run alembic init migrations
```

### 1. Configure Alembic

- In `alembic.ini`: keep `script_location`, and **remove** the hard-coded `sqlalchemy.url` line.
- In `migrations/env.py`:

```python
import app.db.models  # noqa: F401  — registers models on Base.metadata
from app.core.config import get_settings
from app.db.base import Base

config.set_main_option("sqlalchemy.url", get_settings().database_url)
target_metadata = Base.metadata
```

and pass `render_as_batch=True` to both `context.configure(...)` calls (SQLite needs batch mode for ALTERs).

### 2. Revision 1 — the existing table

Create `migrations/versions/0001_create_tasks.py` (`revision = "0001"`, `down_revision = None`) that creates `tasks` exactly as your model defines it today, plus the `ix_tasks_done` index. Downgrade drops both.

> You can draft it with `uv run alembic revision --autogenerate -m "create tasks"` against an **empty** database — then read and tidy the file.

### 3. Revision 2 — due dates

- Model: `due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))`
- Migration `0002_add_due_date.py` (`down_revision = "0001"`): `op.add_column("tasks", sa.Column("due_date", sa.DateTime(timezone=True), nullable=True))`; downgrade drops it with `batch_alter_table`.
- Schemas: `due_date: datetime | None = None` in `TaskCreate` and `TaskUpdate`, `due_date: datetime | None` in `TaskRead`.

Tip: add `use_enum_values=True, validate_default=True` to the input schemas' `model_config` and use plain `model_dump()` in the service, so datetimes stay Python `datetime` objects for SQLAlchemy.

### 4. Remove `create_all`

Delete the `lifespan` that called `Base.metadata.create_all`. From now on: **`uv run alembic upgrade head`** creates/updates the database. Add that command to the README's "Run locally" section.

### 5. Try it

```bash
rm -f taskflow.db
uv run alembic upgrade head
uv run alembic current        # -> 0002 (head)
uv run alembic downgrade -1   # due_date column gone
uv run alembic upgrade head
```

### Checkpoint

The tests point `DATABASE_URL` at a temporary file, run `alembic upgrade head` programmatically, inspect the schema (`tasks`, `due_date`, index, `alembic_version`), run the API on the migrated database (creating a task with a `due_date`), then `downgrade base` and check everything is removed. They also make sure `create_all` is gone from `app/`.
