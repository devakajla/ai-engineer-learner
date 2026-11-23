# Fixtures + dependency overrides

Test the notes API in `app_under_test.py` (import `app`, `get_repo`, `NoteRepo`).

1. Write a **`client` fixture** that:
   - creates a **fresh `NoteRepo()` for every test**
   - installs it with `app.dependency_overrides[get_repo] = ...`
   - yields a `TestClient(app)`
   - clears the overrides afterwards
2. Write tests (using the fixture) for these rules:
   - `POST /notes` → **201** with `{"id", "text", "pinned"}`; empty text → 422
   - `GET /notes` → **pinned notes first**, then by id
   - `PATCH /notes/{id}` changes **only** the fields sent; unknown id → 404
   - `DELETE /notes/{id}` → 204, then the note is gone (404 on PATCH / missing from the list)

Because every test gets a fresh repo, your tests can assume ids start at 1.

**Graded like the previous exercise:** your suite must pass on the correct app and fail on 4 broken versions.
