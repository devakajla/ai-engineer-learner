# FastAPI + SQLAlchemy with a session dependency

Build a small notes API on SQLAlchemy:

- `engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)` (in-memory DB shared across threads — fine for this exercise) and `SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)`
- model `Note` → `notes`: `id`, `text` (`String(500)`), `created_at` (`DateTime(timezone=True)`, `server_default=func.now()`)
- create tables with `Base.metadata.create_all(engine)` at import time (fine here)
- `get_db()` — a **yield** dependency that closes the session
- schemas: `NoteIn(text: str 1–500)`, `NoteOut(id, text, created_at)` with `from_attributes=True`
- routes:
  - `POST /notes` → 201, returns `NoteOut`
  - `GET /notes/{note_id}` → `NoteOut` or 404 `{"detail": "Note not found"}`
  - `GET /notes` → list of `NoteOut`, newest id first

The tests also override `get_db` with their own session.
