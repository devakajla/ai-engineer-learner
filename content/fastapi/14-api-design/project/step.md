# Step 14 — A list endpoint that scales

`GET /api/v1/tasks` returns a bare list, capped at 100, with no way to reach item 101, no search and no sorting. Turn it into a proper collection endpoint.

### The new contract

```
GET /api/v1/tasks?done=false&priority=high&q=report&sort=-due_date&limit=20&offset=40
```

```json
{"items": [ {...TaskRead...} ], "total": 57, "limit": 20, "offset": 40}
```

| param | rules |
|---|---|
| `done`, `priority` | optional filters (as before) |
| `q` | optional, 1–100 chars, case-insensitive match in `title` |
| `sort` | one of `id`, `-id`, `created_at`, `-created_at`, `due_date`, `-due_date`, `title`, `-title`; default **`-id`** (newest first); anything else → 422 |
| `limit` | 1–100, default 20 |
| `offset` | ≥ 0, default 0 |

### 1. A generic envelope — `app/schemas/common.py`

```python
class Page[T](BaseModel):
    items: list[T]
    total: int
    limit: int
    offset: int
```

Reusable for every future list endpoint (users, projects, comments...).

### 2. Sorting safely

- `TaskSort = Literal[...]` in `app/schemas/task.py` — FastAPI rejects anything else with 422.
- In the repository, map names to columns with a whitelist dict (`SORTABLE = {"id": Task.id, ...}`), apply `.desc()` for a leading `-`, and **always add `Task.id` as a tie-breaker** so pages never overlap.

### 3. Repository returns `(items, total)`

Build the filter list once and use it for both queries:

```python
stmt = select(Task).where(*filters).order_by(order, tiebreak).limit(limit).offset(offset)
total = await session.scalar(select(func.count()).select_from(Task).where(*filters))
```

Search with `Task.title.ilike(f"%{q}%")` — SQLAlchemy sends the pattern as a bound parameter.

### 4. Service and route

Pass the new parameters through `TaskService.list(...)`; the route returns `Page[TaskRead]` (`response_model=Page[TaskRead]`).

> This is a **breaking change** for clients of `/api/v1/tasks` (array → object). Since TaskFlow has no external clients yet, we do it in v1. In a live API you'd ship it as `/api/v2/tasks` and keep v1 working.

### Checkpoint

The tests create 25 tasks and check the envelope, `total` with filters, paging through all items exactly once, `q` search, every sort option (including the tie-breaker), and 422 for bad `sort`/`limit`/`offset`.
