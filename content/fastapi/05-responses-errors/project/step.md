# Step 5 — Full CRUD with proper responses

TaskFlow becomes a complete CRUD API: create, list, read, update, delete — with declared response shapes, correct status codes and consistent errors.

### 1. More schemas in `app/schemas/task.py`

```python
class TaskUpdate(BaseModel):
    """PATCH body: every field optional; only the fields sent are changed."""
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    priority: Priority | None = None
    done: bool | None = None


class TaskRead(BaseModel):
    """What the API returns for a task."""
    id: int
    title: str
    description: str | None
    priority: Priority
    done: bool
```

Now you have the classic trio: **Create** (input), **Update** (partial input), **Read** (output).

### 2. Endpoints

| Method + path | Response | Status | Errors |
|---|---|---|---|
| `GET /tasks` | `list[TaskRead]` | 200 | 422 |
| `POST /tasks` | `TaskRead` | **201** | 422 |
| `GET /tasks/{task_id}` | `TaskRead` | 200 | **404**, 422 |
| `PATCH /tasks/{task_id}` | `TaskRead` | 200 | **404**, 422 |
| `DELETE /tasks/{task_id}` | empty | **204** | **404** |

- Use `response_model=...` on every route that returns data.
- Use `status.HTTP_201_CREATED` / `status.HTTP_204_NO_CONTENT`.
- 404 body must be `{"detail": "Task not found"}`.

### 3. Don't repeat yourself

Three routes need "find the task or 404". Write it once:

```python
def get_task_or_404(task_id: int) -> dict[str, Any]:
    ...
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
```

And a reusable annotated type for the path param:

```python
TaskId = Annotated[int, Path(ge=1)]

@app.get("/tasks/{task_id}", response_model=TaskRead, tags=["tasks"])
def get_task(task_id: TaskId):
    return get_task_or_404(task_id)
```

### 4. PATCH correctly

```python
task.update(payload.model_dump(mode="json", exclude_unset=True))
```

Test it in `/docs`: `PATCH {"done": true}` must not erase the title.

### 5. Commit

```bash
git add -A && git commit -m "Complete task CRUD with schemas and status codes"
```

### Checkpoint

The tests run a full lifecycle (create → read → patch → delete → 404), check status codes, check that PATCH only changes sent fields, and that responses never contain extra fields.
