# Interview task: Notes API (25 min)

Build an in-memory CRUD API for notes. Store them in the module-level dict `NOTES: dict[int, dict]` (id → note). A new id is `max(NOTES, default=0) + 1`, so clearing `NOTES` restarts ids at 1.

| Endpoint | Behaviour |
|---|---|
| `POST /notes` body `{"title": str (1-100 chars), "body": str = ""}` | **201** `{"id", "title", "body"}` |
| `GET /notes?limit=10&offset=0` | list of notes ordered by id. `limit` is 1-50 (default 10), `offset` is >= 0. Bad values → 422 |
| `GET /notes/{note_id}` | the note, or **404** `{"detail": "Note not found"}` |
| `PATCH /notes/{note_id}` | update only the fields sent (`title` and/or `body`), return the note. Same 404. Invalid title → 422 |
| `DELETE /notes/{note_id}` | **204** with empty body, or 404 |

Be ready to discuss: why `limit` is capped, PUT vs PATCH, what changes when `NOTES` becomes a database table.
