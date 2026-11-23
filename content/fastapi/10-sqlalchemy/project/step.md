# Step 10 — Move TaskFlow to SQLAlchemy

Raw SQL taught you the fundamentals. Now switch to the **SQLAlchemy ORM** — what nearly every production FastAPI app uses. Thanks to the repository layer, only the storage code changes; routes and services keep their shape.

```bash
uv add sqlalchemy
```

### Target structure

```
app/
├── db/
│   ├── __init__.py
│   ├── base.py           # class Base(DeclarativeBase)
│   ├── models.py         # ORM models (Task)
│   └── session.py        # engine, SessionLocal, get_db()
├── repositories/
│   ├── base.py           # TaskRepository Protocol (returns Task ORM objects now)
│   └── task_repository.py  # SqlAlchemyTaskRepository(session)
└── ...
```

Delete `sqlite_task_repository.py` and the old in-memory repository — dead code is a liability.

### 1. Config

Replace `database_path` with `database_url: str = "sqlite:///./taskflow.db"` (update `.env.example`: `DATABASE_URL=...`). Switching to Postgres later = changing this URL.

### 2. `app/db/models.py`

```python
class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(10), default="medium")
    done: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

### 3. `app/db/session.py`

- One `engine` per process from `get_settings().database_url` (for SQLite add `connect_args={"check_same_thread": False}`).
- `SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)`.
- `get_db()` — a **yield** dependency that always closes the session.

### 4. Repository + DI

- `SqlAlchemyTaskRepository(session)` implements `list / get / add / update / delete` with `select()`, `session.get`, `commit`, `refresh`.
- In `app/api/deps.py`: `DbSession = Annotated[Session, Depends(get_db)]` and `get_task_repository(db: DbSession) -> SqlAlchemyTaskRepository(db)`.

### 5. Schemas

`TaskRead` gets `model_config = ConfigDict(from_attributes=True)` and a new `created_at: datetime` field, so routes can return ORM objects.

### 6. Create tables (temporarily)

Add a `lifespan` to `create_app()` that runs `Base.metadata.create_all(bind=engine)` at startup. Step 11 replaces this with migrations.

### Checkpoint

The tests create a temporary SQLite database, override `get_db`, and run full CRUD through the API (including `created_at`), check the model/table/index, that `get_db` is a yield dependency, and that the repository works directly with a session.
