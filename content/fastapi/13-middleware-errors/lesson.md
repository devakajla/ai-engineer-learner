---
title: Middleware, errors & logging
summary: Do shared jobs once for every request (request IDs, timing, CORS, error handling, logs), instead of repeating them in each route.
plan_ids: [FA-04, BE-09]
---

Some jobs must happen for **every** request: give it an ID, measure how long it took, write a log line, allow your frontend to call the API (CORS), and turn errors into the same JSON shape. If you write this code in each route, it is repetitive, and you will forget it somewhere.

**Middleware** and **exception handlers** do these jobs once, in one place.

## Middleware: code around every request

A **middleware** is a function that wraps your app. It sees the request **before** your route runs, and the response **after** it. Think of a security desk at a building entrance and exit.

```text
request -> [CORS] -> [request id + timing] -> your route -> response -> [request id + timing] -> [CORS] -> client
```

```python
import time
import uuid
from fastapi import Request

@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
    start = time.perf_counter()

    response = await call_next(request)        # run the rest of the app

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-Ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"
    return response
```

How to read it:

- `@app.middleware("http")` registers the function.
- The code **before** `await call_next(request)` runs on the way **in**.
- `call_next(request)` runs the rest of the app (the other middleware and your route) and gives back the response.
- The code **after** it runs on the way **out**. Here it adds two headers to the response.
- The middleware also runs for unknown paths, so a `404` response gets the headers too.

Rules to remember:

- **Order matters.** The middleware added **last** runs **first** (it is the outermost layer).
- Keep middleware **fast and generic**. If something is only for some routes, use a dependency instead (lesson 8).
- To pass a value to your route, store it on `request.state`. For example `request.state.request_id = request_id`. The route can then read `request.state.request_id`.

> Production apps sometimes write "pure ASGI" middleware classes instead of `@app.middleware("http")`, because they are a bit faster and handle streaming better. The idea is the same.

## Worked example: a middleware that adds headers and shares a value

Exercise 1 asks for a middleware that adds response headers and shares a value with the route through `request.state`. Here is the same pattern for a different problem: **count the requests**.

Goal:

- Each request gets a number: 1, 2, 3, and so on.
- The route can read the number.
- The response has a header `X-Request-Number` with the number.

**Step 1.** Keep a counter outside the middleware.

```python
from itertools import count

numbers = count(1)       # 1, 2, 3, ...
```

`next(numbers)` gives the next number.

**Step 2.** Write the middleware. Before `call_next`, take a number and store it on `request.state`.

```python
@app.middleware("http")
async def number_requests(request: Request, call_next):
    request.state.number = next(numbers)
    response = await call_next(request)
    response.headers["X-Request-Number"] = str(request.state.number)
    return response
```

Header values must be text, so use `str(...)`.

**Step 3.** Write the route that reads the value.

```python
@app.get("/me")
def me(request: Request):
    return {"number": request.state.number}
```

**Step 4.** Test it. Notice that an unknown path also gets the header.

```python
client = TestClient(app)
print(client.get("/me").json())                          # -> {'number': 1}
print(client.get("/me").headers["x-request-number"])     # -> 2
print(client.get("/nope").headers["x-request-number"])   # -> 3
```

## Request IDs: following one request through the logs

One user action can touch your API, a background worker and three other services. If every log line carries the same **request ID** (also called a *correlation ID*), you can search the logs for that ID and see the whole story.

The habit:

- If the client sends an `X-Request-ID`, use it. If not, make a new one.
- Put it in every log line.
- Always send it back in the response, so support can ask a user "what is your request ID?".

## CORS

Your frontend may live at `https://app.taskflow.dev` and your API at `https://api.taskflow.dev`. By default, a **browser** will not let JavaScript on one site call another site. This safety rule is called the **same-origin policy**.

The API can give permission with special headers. This is **CORS** (Cross-Origin Resource Sharing). In FastAPI you add `CORSMiddleware`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],   # the frontend address, read from settings
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

- List the exact addresses you trust. Do not use `"*"` together with credentials: browsers reject it, and it is unsafe.
- For some requests, the browser first sends a test request called a **preflight** (method `OPTIONS`). The middleware answers it for you.
- CORS protects **browsers** only. `curl` or another server ignores it. So it is **not** a login system.

## Exception handlers: errors in one place

In lesson 6 your route had to turn a domain error into an HTTP error:

```python
try:
    return await service.get(task_id)
except TaskNotFoundError:
    raise HTTPException(404, "Task not found") from None
```

If every route has this, it is a lot of copy-paste. Instead, register **one handler** for the error type. When any code raises that error, FastAPI calls your handler and sends what it returns.

First, a small family of domain errors (no HTTP inside):

```python
class AppError(Exception):
    code = "app_error"

    def __init__(self, message):
        super().__init__(message)
        self.message = message

class NotFoundError(AppError):
    code = "not_found"

class ConflictError(AppError):
    code = "conflict"
```

Then the handler, which knows HTTP:

```python
from fastapi.responses import JSONResponse

STATUS_FOR = {NotFoundError: 404, ConflictError: 409}

@app.exception_handler(AppError)
async def handle_app_error(request: Request, exc: AppError):
    status = 400                                  # the default
    for error_class, code in STATUS_FOR.items():
        if isinstance(exc, error_class):
            status = code
    return JSONResponse(status_code=status, content={"detail": exc.message, "code": exc.code})
```

Now services raise errors, routes just call services, and one function turns the errors into HTTP. The table `STATUS_FOR` (error type to status code) lives in the **API layer**, not inside the error classes. This keeps the domain free from HTTP.

A route now has no `try`:

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    raise NotFoundError("User not found")

print(TestClient(app).get("/users/1").json())
# -> {'detail': 'User not found', 'code': 'not_found'}
```

### The catch-all handler

An unexpected error (a bug) must also return clean JSON, and must **never** show the real error text or a stack trace to the client.

```python
import logging
logger = logging.getLogger("app")

@app.exception_handler(Exception)
async def handle_unexpected(request: Request, exc: Exception):
    logger.exception("unhandled error")           # the full traceback goes to the LOGS
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "code": "internal_error"},
    )
```

The details go to the log (for you). The client gets only a short message.

### Validation errors

When input is invalid, FastAPI raises `RequestValidationError` (that is the `422`). You can register a handler for it too, to change its shape. Keep the field locations in the answer, so clients can show errors next to form fields.

## Logging that helps at 3 a.m.

**Logging** means writing messages about what the program does. Python's `logging` module does it (Python lesson 26). Here we add the request ID to every line.

A **`ContextVar`** is a variable that holds a **different value for each request**, even when many requests run at the same time. A normal global variable would be mixed up between requests.

```python
import contextvars
import logging

request_id_var = contextvars.ContextVar("request_id", default="-")

class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_var.get()    # add the id to every log record
        return True                                 # True = keep this record
```

Set up the format so the id shows up:

```python
def setup_logging(level="INFO"):
    handler = logging.StreamHandler()
    handler.addFilter(RequestIdFilter())
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(request_id)s] %(name)s: %(message)s"))
    logging.basicConfig(level=level, handlers=[handler], force=True)
```

The middleware sets the value at the start of each request: `request_id_var.set(request_id)`.

Here is a tiny demo with no web server:

```python
setup_logging()
logger = logging.getLogger("demo")

request_id_var.set("abc123")
logger.info("listing notes")
# -> 2026-01-01 10:00:00,000 INFO [abc123] demo: listing notes
```

Good habits in production:

- Write **one log line per request** in the middleware: method, path, status, time, request ID.
- Use **JSON logs** in production, so log tools can filter by field.
- Use levels carefully: client mistakes (4xx) are INFO or WARNING. Server errors (5xx) are ERROR, with the traceback.
- **Never** log secrets, tokens, passwords, or full request bodies with personal data.

## Backend concept: observability

**Observability** means being able to see what your running system is doing. It has three parts:

- **Logs**: what happened.
- **Metrics**: how much and how fast (requests per second, error rate, slow requests).
- **Traces**: the path of one request across many services (for example with OpenTelemetry).

The request ID and timing header you wrote today are the first seed of all three. For AI apps you will also record each model call: tokens used, time taken and cost.

## A little deeper (optional)

- A `Filter` added to a **logger** only applies to records created by **that** logger, not by its children. To put the request ID on every record in the whole app, attach the filter to the **handler**, or use a log record factory. The project step shows the factory way.
- Use `ContextVar.reset(token)` at the end of a request to put the old value back. `set()` gives you the token.
- `from None` in `raise HTTPException(...) from None` hides the original error from the traceback. It is optional.

## Common mistakes

- Copy-pasting `try/except` and `HTTPException` into every route.
- Sending stack traces or raw exception text in a 500 response.
- `allow_origins=["*"]` with credentials.
- Slow work in middleware. It runs on every request.
- Logs without a request ID. Under load you cannot follow one request.

## Interview corner

- **Q: What is middleware? Give some examples.** Code that wraps every request and response. Examples: CORS, request IDs, timing, compression, logging.
- **Q: How do you return consistent errors in FastAPI?** Raise domain errors, and register `@app.exception_handler` functions that turn them into JSON. Add a catch-all for 500 that logs the error and hides the details.
- **Q: What is CORS? Does it secure your API?** It is a browser rule that lets a server allow calls from other origins. It is not authentication: tools other than browsers ignore it.
- **Q: How do you follow one request through the logs?** A request ID set in middleware, kept in a `ContextVar`, added to every log record, and returned in a response header.

## Summary

- `@app.middleware("http")` wraps every request. The last one added runs first.
- Add a request ID and timing headers, and write one access log line per request.
- Use `CORSMiddleware` with the allowed origins taken from settings.
- Domain errors go to one `exception_handler`, which returns consistent JSON. A catch-all 500 handler logs the error and hides the details.
- A `ContextVar` plus a logging filter puts the request ID in every log line.
