# Step 4 — Create tasks with a schema

Clients can now **create** tasks. The request body is described by a Pydantic schema that lives in its own module — the first step towards a clean structure.

### 1. Create `app/schemas/`

```
app/
├── __init__.py
├── main.py
└── schemas/
    ├── __init__.py
    └── task.py
```

### 2. In `app/schemas/task.py`

- **Move** the `Priority` enum here (and import it in `main.py`) — one source of truth.
- Add `TaskCreate`:

| Field | Type | Rules |
|---|---|---|
| `title` | `str` | 1–200 chars, whitespace stripped |
| `description` | `str \| None` | optional, max 2000 chars |
| `priority` | `Priority` | default `medium` |

- Reject unknown fields and strip whitespace:

```python
model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
```

Note what is **not** in `TaskCreate`: `id` and `done`. The server controls those (remember *mass assignment*).

### 3. `POST /tasks` in `app/main.py`

- Take `payload: TaskCreate`.
- New id = highest existing id + 1.
- Store `{"id": ..., **payload.model_dump(mode="json"), "done": False}` in `TASKS` and return it.

`model_dump(mode="json")` turns the `Priority` enum into the plain string `"medium"`, so stored tasks look like the seed data.

### 4. Try it in `/docs`

Open `/docs`, expand `POST /tasks`, click *Try it out*. Send a valid task, then break it on purpose (empty title, `"priority": "urgent"`, an extra `"done": true`) and read the 422 responses.

### Checkpoint

The tests create a task, read it back by id, check the defaults, and send invalid payloads (empty or whitespace title, bad priority, unknown fields) expecting 422. They also check that `TaskCreate` lives in `app/schemas/task.py`.
