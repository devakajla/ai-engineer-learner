# Step 3 — List and read tasks

TaskFlow gets its first real resource: **tasks**. We keep them in a Python list for now (Level 2 swaps it for a database without changing the API).

A task looks like this:

```json
{"id": 1, "title": "Set up TaskFlow", "description": null, "priority": "high", "done": true}
```

### 1. Add a `Priority` enum and seed data in `app/main.py`

```python
class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

# Temporary in-memory storage. A real database replaces this in Level 2.
TASKS: list[dict[str, Any]] = [
    {"id": 1, "title": "Set up TaskFlow", "description": None, "priority": "high", "done": True},
    {"id": 2, "title": "Learn path parameters", "description": None, "priority": "medium", "done": False},
    {"id": 3, "title": "Write the README", "description": "Explain how to run the API", "priority": "low", "done": False},
]
```

### 2. `GET /tasks` — list with filters

Query parameters:

| Param | Type | Default | Rule |
|---|---|---|---|
| `done` | `bool \| None` | `None` | filter by done state |
| `priority` | `Priority \| None` | `None` | filter by priority |
| `limit` | `int` | `20` | 1–100 |

Examples: `/tasks?done=false`, `/tasks?priority=high`, `/tasks?limit=2`.

### 3. `GET /tasks/{task_id}` — read one

- `task_id` is an `int` ≥ 1 (`Path(ge=1)`).
- If no task has that id, raise `HTTPException(status_code=404, detail="Task not found")`. (Lesson 5 covers errors properly — for now just use this line.)

### Best practices for this step

- Use `tags=["tasks"]` on both routes so `/docs` groups them.
- Add **return type hints** (`-> list[dict[str, Any]]`).
- Keep the filtering readable: one `if` per filter.

### Try it

```bash
uv run fastapi dev app/main.py --port 8001
curl "http://127.0.0.1:8001/tasks?done=false&limit=1"
curl -i http://127.0.0.1:8001/tasks/99
```

### Checkpoint

The tests call `/tasks` with each filter, check the `limit` bounds (0 and 101 must be 422), read a task by id, and expect 404 / 422 for missing or invalid ids.
