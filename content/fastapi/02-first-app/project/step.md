# Step 2 — The app object and a health check

Every production API has a **health endpoint**. Load balancers, Kubernetes and uptime monitors call it every few seconds; if it stops answering `200`, traffic is moved away from that instance.

### 1. Create `app/main.py`

```python
from fastapi import FastAPI

app = FastAPI(
    title="TaskFlow",
    version="0.1.0",
    description="A task-manager REST API",
)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    """Liveness check used by load balancers and monitoring."""
    return {"status": "ok"}
```

- `tags=["health"]` groups the endpoint in `/docs`.
- The **return type hint** documents the response and helps your editor.
- The docstring appears in the docs as the endpoint description.

### 2. Run it

```bash
uv run fastapi dev app/main.py
```

Open http://127.0.0.1:8000/docs and call `/health` from Swagger UI. Then try:

```bash
curl -i http://127.0.0.1:8000/health
```

Look at the status line and the `content-type` header — connect it to lesson 1.

> The Learner backend also runs on port 8000. If it's running, start TaskFlow on another port: `uv run fastapi dev app/main.py --port 8001`.

### 3. Commit

```bash
git add -A && git commit -m "Add FastAPI app with health check"
```

Small, focused commits are a habit worth building now.

### Expected structure

```
taskflow/
├── app/
│   ├── __init__.py
│   └── main.py
├── .gitignore
├── pyproject.toml
├── README.md
└── uv.lock
```

### Checkpoint

The hidden tests import `app` from `app.main`, check the title/version, and call `GET /health`.
