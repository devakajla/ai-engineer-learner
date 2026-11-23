# A service layer with domain errors

The starter gives you a repository. Build the layers above it:

**1. Service** — `NoteService(repo)` with:

- `create(title: str) -> dict` — raises `DuplicateNoteError` if a note with the same title already exists (**case-insensitive**), otherwise `repo.add(title)`.
- `get(note_id: int) -> dict` — raises `NoteNotFoundError` if missing.

The service must **not** import or raise anything from FastAPI.

**2. Routes** — using a module-level `service = NoteService(InMemoryNoteRepository())`:

| Request | Success | Error |
|---|---|---|
| `POST /notes` body `{"title": "..."}` | 201 + the note | 409 `{"detail": "Note already exists"}` |
| `GET /notes/{note_id}` | 200 + the note | 404 `{"detail": "Note not found"}` |

The routes translate the domain errors into HTTP errors.
