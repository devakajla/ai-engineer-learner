# App metadata

Good APIs describe themselves. Create `app` so that:

1. The OpenAPI docs show title **`TaskFlow`**, version **`0.1.0`** and description **`Manage your tasks`** (pass them to `FastAPI(...)`).
2. `GET /about` returns `{"name": "TaskFlow", "version": "0.1.0"}` — read the values **from the app object** (`app.title`, `app.version`) instead of typing them twice.

The tests read `/openapi.json` to check the metadata.
