# Answers to the exercises

Try each exercise yourself first. Short answers for "think" questions, code for the rest.

## Chapter 1

1. Route, then service, then repository (then the database).
2. (a) a password-strength check is a business rule: **service** (or `core` if it is a shared tool). (b) the SQL for a task by id: **repository**. (c) the code that returns `404`: **route**, or an exception handler in the API layer.
3. `uv --version` prints a version number such as `uv 0.x.y`.

## Chapter 2

1. `@app.get("/hello")` and `def hello(): return {"message": "Hello, FastAPI"}`.
2. The same shape: `{"version": "1.0.0"}`.
3. It prints the installed FastAPI version.
4. The **first** one defined runs. FastAPI matches routes in order.
5. Reload helps development (code changes show at once) but watches files and restarts, which costs resources and drops requests. Production should be stable and use fixed processes.

## Chapter 3

1. `if q: tasks = [t for t in tasks if q.lower() in t["title"].lower()]`.
2. `return tasks[offset: offset + limit]` with `offset: Annotated[int, Query(ge=0)] = 0`.
3. Above `/tasks/{task_id}` it works. Below, `summary` is read as a `task_id`, fails to become an int and you get `422`.
4. `class Order(str, Enum): asc = "asc"; desc = "desc"`, then `sorted(tasks, key=lambda t: t["id"], reverse=(order == Order.desc))`.
5. The filter is a **property of the collection**, not a different resource. Query parameters combine (`?done=true&limit=5`), and the path stays stable.

## Chapter 4

1. `due_in_days: int | None = Field(default=None, ge=1, le=365)`.
2. A `field_validator("tags")` that returns `list(dict.fromkeys(t.lower() for t in value))` (keeps order, removes duplicates).
3. `loc` shows `["body", "tags"]`, and the message says the input should be a valid list.
4. Find the task, `tasks.remove(task)` and return `Response(status_code=204)`.
5. The server creates the id. If the client could send it, it could overwrite or clash with other tasks.

## Chapter 5

1. Look the task up and `raise TaskNotFound(task_id)` when it is `None`.
2. `class DuplicateTitle(Exception)`, raised in the service, with a handler returning `JSONResponse(status_code=409, content={"error": "duplicate_title", "message": ...})`.
3. `class UserOut(BaseModel): id: int; email: str` (no `password`) used as `response_model`.
4. `@router.get("/{task_id}", response_model=TaskOut, responses={404: {"description": "Task not found"}})`.
5. The service then does not depend on HTTP, so it can be reused (a worker, a CLI) and tested without a web layer. One place (the handler) decides the status code.

## Chapter 6

1. (a) `schemas/`, (b) `core/security.py`, (c) `services/`, (d) `repositories/`, (e) `api/routes/`.
2. In `config.py`: `max_tasks: int = 100`. In the service, count the tasks and `raise TaskLimitReached()`. Handler: `JSONResponse(status_code=409, ...)`.
3. The arrow from `repositories` or `services` back up to `api` must never exist (imports go downward only).
4. Touched: the new `routes/version.py` and `api/router.py` (to include it). Nothing else.
5. It means the route only handles HTTP and hands rules to the service, so the rules live in one place.

## Chapter 7

1. `def get_request_id(x_request_id: Annotated[str | None, Header()] = None): return x_request_id or uuid.uuid4().hex[:8]`.
2. Read `settings.max_limit` inside `Pagination` with `Depends(get_settings)` and use it in `le=` through a manual check (or `min(limit, max_limit)`).
3. `APIRouter(prefix="/tasks", dependencies=[Depends(require_admin_key)])`. Without the header you get `401` or `403`.
4. `app.dependency_overrides[get_task_repo] = lambda: FakeRepo(5 tasks)`, call the list route, and expect five items. Clear the overrides after.
5. A repository created at import time is shared and hard to replace. `Depends` creates it per request and the framework lets a test swap it.

## Chapter 8

1. Add the column, run `alembic revision --autogenerate -m "add due date"`, read the file (`op.add_column`), then `alembic upgrade head`.
2. Repository: `select(func.count()).select_from(Task).where(Task.owner_id == owner_id)`. Service: a thin `count_tasks`. Route: `GET /tasks/count` (declare it **above** `/{task_id}`).
3. `downgrade -1` removes the last change (the column or the tables). `upgrade head` brings it back. The `alembic_version` row changes each time.
4. Existing rows have no value for the new column. A non-null column without a default would make the migration fail.
5. A `403` confirms the task exists. A `404` reveals nothing about other users' data.

## Chapter 9

1. About 1 second, because all four waits overlap.
2. `/bad2` with `await asyncio.sleep(2)` does not block, so three requests take about 2 seconds. `time.sleep` blocks the loop.
3. `asyncio.TimeoutError` (a `TimeoutError`).
4. 9 tasks, 3 at a time, 1 second each: about 3 seconds.
5. Declare the route with plain `def`, or call it with `run_in_threadpool`. Or move it to a queue and worker.

## Chapter 10

1. In the middleware: `response.headers["X-Process-Time"] = f"{ms:.1f}"`.
2. `if ms > 500: logger.warning("slow request %s %.0f ms", request.url.path, ms)`.
3. The client sees `{"error":"internal_error","message":"Something went wrong"}` with status 500. The log shows the full traceback.
4. `app.add_middleware(GZipMiddleware, minimum_size=1000)`. The compressed response is much smaller if the client sends `Accept-Encoding: gzip`.
5. CORS only instructs browsers. Anyone can call your API without a browser, so you still need real authentication.

## Chapter 11

1. A `PATCH /auth/me` with `UserUpdate(email)`. Errors: `409` (email taken), `422` (bad email), `401` (no token).
2. Register two users, create a task as user A, call `DELETE /tasks/{id}` with user B's token: expect `404`, and the task still exists for A.
3. A `401 Invalid or expired token`.
4. A migration adds `role: Mapped[str] = mapped_column(default="user", server_default="user")`. The `require_role` dependency raises `403` when the role differs.
5. Table `refresh_tokens(id, user_id, token_hash, expires_at, revoked)`. `POST /auth/login` returns both tokens. `POST /auth/refresh` checks the hash, expiry and revoked flag, then returns a new access token (and often a new refresh token). `POST /auth/logout` marks it revoked. Store only a hash.
6. Different messages tell attackers which emails exist.

## Chapter 12

1. `background.add_task(log_welcome, user.email)` in the register route, where `log_welcome` calls `logger.info("welcome email to %s", email)`.
2. At the start of the job: `if ctx["job_try"] == 1: raise Retry(defer=2)`. The log shows try 2.
3. `enqueue_job("make_report", user.id, _job_id=f"report:{user.id}:{minute}")` with `minute = int(time.time()) // 60`. If it returns `None`, answer `409`.
4. Open a session with `SessionLocal()` inside the job, load the `Task` by id, log its title. Never pass the request's session into a job.
5. A **payment receipt** must use a queue (it must not be lost). Image resizing should too (it is slow and CPU heavy). A log line is fine with `BackgroundTasks`.

## Chapter 13

1. `yield ServerSentEvent(data=i, event="tick")` (import from `fastapi.sse`).
2. A fake class whose `create` is async and returns an object that supports `async for` and gives chunks with `.choices[0].delta.content`. Collect with `[p async for p in stream_answer(...)]`.
3. An async generator that yields the header, then one line per task, returned with `StreamingResponse(gen(), media_type="text/csv")`.
4. Use the `ConnectionManager` class from the chapter. `connect`, loop on `receive_text`, `broadcast`, and `disconnect` in `except WebSocketDisconnect`.
5. You keep paying for tokens nobody reads. Stop the generation when the client disconnects.

## Chapter 14

1. `if len(data) > 200_000: raise HTTPException(413, ...)` with `MAX_BYTES = 200_000`.
2. `files: list[UploadFile]`, loop over them, and return a list of `{"filename", "size"}`.
3. `name = uuid.uuid4().hex + suffix`. A random name cannot clash or overwrite and cannot contain the attacker's text.
4. Read `visited: Annotated[str | None, Cookie()] = None`. If missing, `response.set_cookie("visited", "1")` and return a first message. Otherwise return `"welcome back"`.
5. The client controls it. Anyone can label a harmful file as `image/png`.

## Chapter 15

1. `PATCH` then `GET` shows `done` true. `DELETE` returns 204 and the next `GET` returns 404.
2. Register twice with the same email, and check the second status is `409`.
3. Log in with a wrong password and expect `401`.
4. `@pytest.mark.parametrize("body", [{"email": "a@x.com", "password": "short"}, {"email": "bad", "password": "secret123"}])` then expect `422`.
5. `app.dependency_overrides[get_llm_client] = lambda: FakeClient(["a", "b"])`. Call the route with auth and check the body contains the pieces.
6. Each new connection to an in-memory SQLite database gets its own empty database. `StaticPool` keeps a single connection so every session sees the same tables.

## Chapter 16

1. Docker shows `CACHED` for the dependency layers and rebuilds only the layers after the changed code.
2. `/ready` returns `503` when the database is not reachable.
3. State in memory (an in-memory cache, a WebSocket list) is not shared across replicas, so users see inconsistent results.
4. One line per setting, for example `DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/app` and `SECRET_KEY=change-me`.
5. Add a step `- run: uv run ruff check` (add `ruff` as a dev dependency).
6. The new code expects the new schema. If the schema is old, requests fail. Old code must keep working with the new schema for a moment, so use compatible (additive) migrations.

## Chapter 17

1. A client that counts calls and raises `TimeoutError` for the first two. Monkeypatch `asyncio.sleep` with an async no-op. Assert the third call result is returned and the count is 3.
2. A `FakeRedis` with `incr` (a dict counter) and `expire` (no-op). Call the route 11 times and check the 11th gives `429`.
3. The fake client returns `"not json"` then `'{"title":"Buy milk","priority":2}'`. Assert the result is a `TaskIdea` and the client was called twice.
4. For example input 1 dollar per million tokens and output 3 dollars per million: `500/1e6*1 + 200/1e6*3 = 0.0005 + 0.0006 = 0.0011` dollars.
5. Any route that spends money or exposes private data without login. Anonymous users can drain your budget.

## Chapter 18

1. Follow the ten steps. Commit after each slice.
2. A good README: requirements, `uv sync`, copy `.env.example` to `.env`, `alembic upgrade head`, `uv run fastapi dev app/main.py`, `uv run pytest`, and an example `curl`.
3. Steps that were missing or unclear are the README's bugs. Fix them.
4. `max_bookmarks: int = 500` in Settings, `class BookmarkLimitReached(Exception)`, raised in the service, and a handler returning `409`.
5. Usually step 3 (design the API) and step 5 (one slice end to end). Without them people build wide and discover structure problems late, when they are expensive to fix.

## Interview coding questions (chapter 19)

**1. Item not found**

```python
@app.get("/items/{item_id}")
async def get_item(item_id: int):
    item = ITEMS.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
```

**2. API key dependency**

```python
async def require_api_key(x_api_key: Annotated[str | None, Header()] = None):
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
```

**3. Signup model**

```python
class Signup(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8)
    age: int = Field(ge=18, le=120)
```
