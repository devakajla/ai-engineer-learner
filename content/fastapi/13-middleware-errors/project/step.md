# Step 13 — Errors, middleware, CORS and logging

Make TaskFlow production-friendly: every response carries a request ID and timing, every error has the same shape, unexpected errors never leak internals, and every log line can be traced to a request.

### Target structure (new files)

```
app/
├── api/
│   ├── errors.py        # domain error → HTTP mapping + handlers
│   └── middleware.py    # request id, timing, access log
└── core/
    ├── errors.py        # AppError, NotFoundError, ConflictError (no HTTP!)
    └── logging.py       # request_id_var, RequestIdFilter, setup_logging()
```

### 1. Domain errors — `app/core/errors.py`

`AppError(message)` with a `code` class attribute; `NotFoundError(code="not_found")`, `ConflictError(code="conflict")`. Make `TaskNotFoundError` a subclass of `NotFoundError` with the message `"Task not found"`.

### 2. Handlers — `app/api/errors.py`

- `STATUS_FOR = {NotFoundError: 404, ConflictError: 409}`; other `AppError`s → 400.
- Response body: `{"detail": exc.message, "code": exc.code}`.
- Catch-all `Exception` → 500 `{"detail": "Internal server error", "code": "internal_error"}` and `logger.exception(...)`.
- `register_exception_handlers(app)` wires both.

Then **delete every `try/except TaskNotFoundError`** from `app/api/routes/tasks.py` — routes just `return await service.get(task_id)`.

### 3. Logging — `app/core/logging.py`

A `ContextVar` `request_id_var` and `setup_logging(level)` with the format `"%(asctime)s %(levelname)s [%(request_id)s] %(name)s: %(message)s"`. Use logger names under `taskflow.` (e.g. `taskflow.access`, `taskflow.errors`).

Every record needs a `request_id` attribute. A filter only runs for the logger/handler it's attached to (filters on a parent logger don't apply to child loggers!), so the most robust way is a **log record factory**:

```python
_base_factory = logging.getLogRecordFactory()

def _record_factory(*args, **kwargs):
    record = _base_factory(*args, **kwargs)
    record.request_id = request_id_var.get()
    return record

logging.setLogRecordFactory(_record_factory)   # inside setup_logging()
```

### 4. Middleware — `app/api/middleware.py`

`register_middleware(app)` adds an HTTP middleware that:
- takes `X-Request-ID` from the request or generates `uuid4().hex`, sets `request_id_var` (and resets it at the end),
- adds `X-Request-ID` and `X-Process-Time-Ms` headers,
- logs one INFO line: `GET /api/v1/tasks -> 200 (3.1 ms)` on logger `taskflow.access`.

### 5. CORS + settings

`Settings.cors_origins: list[str] = ["http://localhost:3000"]` and `log_level: str = "INFO"` (document both in `.env.example`). Add `CORSMiddleware` in `create_app()` using `settings.cors_origins`.

### Checkpoint

The tests check the 404 body `{"detail": "Task not found", "code": "not_found"}`, that routes have no `try/except`, a hidden 500 handler (no secrets in the body), request-ID echo/generation and timing headers, the access log line carrying the request ID, and a CORS preflight from `http://localhost:3000`.
