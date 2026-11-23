# Step 1 — Create the TaskFlow project

**TaskFlow** is the API you'll build across this whole track: users, tasks, auth, a database, background jobs, caching, Docker. Today you only set up the project the way a professional team would.

### 1. Create the project with uv

```bash
cd ~/Projects
uv init taskflow --app
cd taskflow
uv add "fastapi[standard]"
```

- `uv init --app` creates `pyproject.toml`, `.python-version`, `README.md`, `.gitignore`, a demo `main.py`, and a git repo.
- `uv add` writes the dependency into `pyproject.toml`, pins exact versions in `uv.lock`, and installs into `.venv/`.
- `fastapi[standard]` includes `uvicorn` (the server), the `fastapi` CLI and `httpx` (for tests).

> Commit `uv.lock` to git — it makes installs reproducible for every developer and in CI.

### 2. Create the application package

All app code lives in one package called `app`:

```bash
rm main.py            # we won't use the demo file
mkdir app
touch app/__init__.py # makes "app" an importable package
```

Why a package and not loose files? Imports become explicit (`from app.schemas.task import TaskCreate`), tests can import the app, and the structure scales.

### 3. Check `.gitignore`

It must ignore at least the virtual environment and Python caches:

```gitignore
.venv/
__pycache__/
*.pyc
.env
```

`.env` will hold secrets later — **never commit it**.

### 4. Write a README

Replace the generated `README.md` with a short description. It must mention **TaskFlow**. A good template:

```markdown
# TaskFlow

A task-manager REST API built with FastAPI.

## Run locally
uv run fastapi dev app/main.py

## Planned endpoints
- GET /health
- GET /tasks, POST /tasks
- GET /tasks/{id}, PATCH /tasks/{id}, DELETE /tasks/{id}
```

### Expected structure

```
taskflow/
├── app/
│   └── __init__.py
├── .gitignore
├── .python-version
├── pyproject.toml
├── README.md
└── uv.lock
```

### Check it

Your project folder is set below the step (default `~/Projects/taskflow`). Press **Check my project**: hidden tests look at your folder, then Claude reviews it.
