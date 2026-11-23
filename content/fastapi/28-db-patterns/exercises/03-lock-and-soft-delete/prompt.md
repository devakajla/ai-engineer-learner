# Two editors, one note

Two people open the same note, and both press Save. Without protection the second save **silently overwrites** the first. Fix this with an **optimistic lock**, and add **soft delete**. With SQLAlchemy 2.0 (no FastAPI), write:

- `class Base(DeclarativeBase)`
- `class StaleVersion(Exception)`
- model `Note` → `notes`: `id`, `title` (`String(200)`, required), `version` (int, default `1`), `deleted` (bool, default `False`)
- `add_note(session, title) -> Note` (commit + refresh)
- `update_title(session, note_id, expected_version, title) -> Note`
  - Changes the title **only if** the stored `version` equals `expected_version`, and then adds 1 to `version`. Return the fresh note.
  - If the version differs, raise `StaleVersion`.
  - If the note does not exist or is deleted, raise `LookupError`.
- `soft_delete(session, note_id) -> bool`: set `deleted = True` and keep the row. `False` if it does not exist or is already deleted.
- `list_notes(session) -> list[Note]`: notes that are not deleted, ordered by id.

```text
note v1.  A saves (expected 1)  -> ok, now v2
          B saves (expected 1)  -> StaleVersion   (B must reload first)
```

**Think first:** Why is "read the note, check the version in Python, then write" not safe? What can happen between the read and the write?

**Hint:** Let the database do the check in **one statement**: `update(Note).where(Note.id == note_id, Note.version == expected_version, Note.deleted.is_(False)).values(title=title, version=Note.version + 1)`, then look at `result.rowcount`. When it is `0`, find out which reason applies.
