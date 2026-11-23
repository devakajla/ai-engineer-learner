# 10. Middleware, CORS, logging and app lifecycle

Some things must happen for **every** request: add a request id, measure time, write a log line, allow a website to call you. You do not want to copy that code into each route. Middleware does it in one place.

This chapter also covers errors you did not plan for, and starting and stopping your app cleanly.

## Idea: middleware wraps every request

@@ flow | Figure 10.1: a request passes through the middleware, then the route, and the response comes back the same way.
Middleware|before: start timer;add request id|blue -> Route|does the real work|green -> Middleware|after: log time;add header|blue
@@ end

## Steps

::: {.step}
Step 1: logging setup
:::

Never use `print` in a backend. Use the `logging` module: it has levels, timestamps and can be sent to files or services.

`app/core/logging.py`:

```python
import logging


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
```

Anywhere in your code:

```python
import logging
logger = logging.getLogger(__name__)

logger.info("task created id=%s", 5)
logger.warning("slow query took %s ms", 900)
logger.error("payment failed for order %s", 12)
```

Use `%s` placeholders and pass values as arguments. Python formats the string only if the log line is actually printed.

::: {.step}
Step 2: lifespan: start and stop
:::

Some work must run **once** at startup (connect to things, load a model) and once at shutdown (close connections). FastAPI uses a **lifespan** function for both:

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("starting up")
    yield                          # the app runs while we are paused here
    logger.info("shutting down")   # runs when the server stops
```

Everything before `yield` is startup. Everything after is shutdown. Pass it to the app: `FastAPI(lifespan=lifespan)`. You can also store shared objects on `app.state` (for example a Redis client) and reach them from routes through `request.app.state`.

::: {.step}
Step 3: a middleware for request id and timing
:::

In `create_app()` (in `main.py`):

```python
import time
import uuid

from fastapi import Request

@app.middleware("http")
async def request_id_and_timing(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", uuid.uuid4().hex[:8])
    start = time.perf_counter()
    response = await call_next(request)          # run the route
    ms = (time.perf_counter() - start) * 1000
    response.headers["X-Request-ID"] = request_id
    logger.info("%s %s -> %s (%.1f ms) id=%s",
                request.method, request.url.path, response.status_code, ms, request_id)
    return response
```

`call_next(request)` means "now run the rest (the route) and give me its response". Code before it runs on the way in. Code after it runs on the way out.

Why a **request id**? When a user says "my request failed", you can find every log line for that one request. Clients can send their own `X-Request-ID`, and we send it back.

Run the server and call `/health`. The logs show:

```
2026-11-22 01:12:05,209 INFO taskflow starting up
2026-11-22 01:12:10,192 INFO taskflow GET /health -> 200 (1.2 ms) id=1da26c6a
2026-11-22 01:12:10,360 INFO taskflow shutting down
```

(When you press `Ctrl+C`, the last line appears.) And the response has the header:

```bash
curl -i localhost:8000/health
# -> x-request-id: 1da26c6a
```

::: {.step}
Step 4: CORS
:::

A **browser** blocks a web page from calling an API on a different address (origin), unless the API says it is allowed. The rule is called CORS. If your frontend runs on `http://localhost:3000` and your API on `http://localhost:8000`, you must allow it:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,   # ["http://localhost:3000"]
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Add `cors_origins: list[str] = ["http://localhost:3000"]` to `Settings`. In production set it to your real site only.

Test it:

```bash
curl -i localhost:8000/health -H "Origin: http://localhost:3000"
# -> access-control-allow-origin: http://localhost:3000
curl -i localhost:8000/health -H "Origin: http://evil.com"
# -> (no access-control-allow-origin header)
```

> CORS protects **browser users**. It does not stop `curl` or scripts. It is not a security tool for your API. Never use `allow_origins=["*"]` together with cookies or credentials.

::: {.step}
Step 5: a catch-all for surprises
:::

Bugs happen. By default, an unhandled error returns a plain `500 Internal Server Error`. You can make it a consistent JSON and log the details privately:

```python
@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    logger.exception("unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "message": "Something went wrong"},
    )
```

`logger.exception` writes the full stack trace to your logs. The **client** sees a short message only. Never send stack traces to users: they reveal how your code works.

Our own handler from earlier chapters stays:

```python
@app.exception_handler(TaskNotFound)
async def task_not_found_handler(request: Request, exc: TaskNotFound):
    return JSONResponse(status_code=404, content={"error": "not_found", "message": str(exc)})
```

FastAPI picks the **most specific** handler for the error.

::: {.step}
Step 6: a better home for it
:::

`main.py` is getting long again. Move the pieces:

```
app/core/logging.py          setup_logging()
app/core/middleware.py       request_id_and_timing (a function that adds it to the app)
app/core/handlers.py         register_exception_handlers(app)
```

For example `app/core/handlers.py`:

```python
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import TaskNotFound

logger = logging.getLogger("taskflow")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(TaskNotFound)
    async def task_not_found(request: Request, exc: TaskNotFound):
        return JSONResponse(status_code=404, content={"error": "not_found", "message": str(exc)})

    @app.exception_handler(Exception)
    async def unhandled(request: Request, exc: Exception):
        logger.exception("unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content={"error": "internal_error", "message": "Something went wrong"},
        )
```

Then `create_app()` just calls `register_exception_handlers(app)`. This is the same lesson as chapter 6: when `main.py` grows, give each concern a file. (The reference project at the end of the booklet keeps these small ones inside `main.py`, which is also fine. Move them when it hurts.)

## Middleware order

Middleware added **last** runs **first** on the way in. If CORS must answer even for errors, it should be the **outermost**. In practice: add CORS last, or test with a browser.

## Other useful built-ins

| Middleware | Use |
| --- | --- |
| `GZipMiddleware(minimum_size=1000)` | compress big responses |
| `TrustedHostMiddleware(allowed_hosts=[...])` | reject requests for the wrong `Host` header |
| `HTTPSRedirectMiddleware` | send HTTP users to HTTPS |

## Docs metadata

Make `/docs` friendly:

```python
app = FastAPI(
    title="TaskFlow",
    version="1.0.0",
    description="A small task manager API.",
    lifespan=lifespan,
)
```

::: {.box .checkpoint}
**Folder now**

```
app/
├── main.py            # create_app: lifespan, CORS, middleware, handlers, routers
├── core/
│   ├── config.py      # + cors_origins
│   ├── exceptions.py
│   └── logging.py     # NEW
└── ...
```

**Checkpoint:** `curl -i localhost:8000/health` shows an `x-request-id` header, and your terminal logs `GET /health -> 200 (... ms) id=...`.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Using `print` instead of `logging`.
- Logging passwords, tokens, or whole request bodies.
- CORS `allow_origins=["*"]` in production.
- Heavy work in a middleware. It runs on **every** request.
- Sending stack traces to clients.
- Forgetting that middleware order matters.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: What is middleware?**
Code that wraps every request and response, for cross-cutting jobs like logging, request ids, CORS and compression.

**Q: What is `lifespan` for?**
Running code once at startup and shutdown, such as opening and closing connections. It replaced the old `on_event` hooks.

**Q: What is CORS and does it secure your API?**
A browser rule that blocks cross-origin calls unless the server allows the origin. It protects browser users only, not your API from scripts.

**Q: How do you handle errors you did not expect?**
Register a catch-all `Exception` handler that logs the stack trace and returns a safe, generic message.

**Q: Why log a request id?**
To follow one request through all log lines and across services.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Add a middleware that adds the header `X-Process-Time` with the milliseconds.
2. Log a `WARNING` for any request that takes longer than 500 ms. Test with a route that sleeps 1 second.
3. Create a route that does `1 / 0`. Call it and check what the client sees and what the log shows.
4. Add `GZipMiddleware` and compare the size of a large response with and without it (`curl -s ... | wc -c`).
5. **Think:** why is CORS not a replacement for authentication?
:::
