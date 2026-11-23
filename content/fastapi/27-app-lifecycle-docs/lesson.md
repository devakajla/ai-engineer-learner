---
title: "App lifecycle, lifespan & API docs"
summary: Run code when the app starts and stops (lifespan), share things through app.state, mount sub-apps, add GZip and host checks, and shape the OpenAPI docs.
plan_ids: [FA-01, FA-07]
---

An app has a **life**: it starts, it serves requests for hours or days, and then it stops. Some things should be made **once** at the start and cleaned up at the end: a database engine, an HTTP client, a loaded AI model.

This lesson shows how to do that with **lifespan**. It also covers a few small tools that every real app uses: sub-apps, compression, a host check, and tidy API docs.

## Lifespan: startup and shutdown

A **lifespan** is a function with one `yield`. Code **before** `yield` runs once at startup. Code **after** it runs once at shutdown.

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("starting")        # startup
    yield                    # the app runs here and serves requests
    print("stopping")        # shutdown

app = FastAPI(lifespan=lifespan)
```

- `@asynccontextmanager` turns the function into something FastAPI can enter and exit. You only need to copy this shape.
- The `yield` has the same idea as `yield` dependencies (lesson 8): set-up before, clean-up after. The difference is that a dependency runs for each **request**, and a lifespan runs once for the whole **app**.

The older way, `@app.on_event("startup")`, still works but is deprecated. Use `lifespan`.

### Sharing things: `app.state`

`app.state` is an empty object where you can store your own values. Put things there at startup, read them in routes through `request.app.state`:

```python
from fastapi import Request

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.visits = 0
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/visit")
def visit(request: Request):
    request.app.state.visits += 1
    return {"visits": request.app.state.visits}
```

A `Request` parameter gives you the current request. `request.app` is the app that handles it.

Why not a global variable? A global is created when the file is imported, which makes it hard to replace in tests, and it has no clean shutdown. State created in the lifespan starts and stops together with the app.

### Testing the lifespan

`TestClient` runs the lifespan **only** inside a `with` block:

```python
from fastapi.testclient import TestClient

with TestClient(app) as client:        # startup runs here
    print(client.get("/visit").json())   # -> {'visits': 1}
    print(client.get("/visit").json())   # -> {'visits': 2}
                                         # shutdown runs when the block ends
```

Without `with`, startup never runs and `app.state.visits` does not exist. This is a very common surprise.

## Worked example: a resource that lives as long as the app

Exercise 1 asks for startup and shutdown steps and a counter in `app.state`. Here is the same pattern for a different problem: a **settings dictionary and a log of opened and closed resources**.

Goal:

- At startup, record `"open"` in a list `LOG`, and put `{"currency": "INR"}` in `app.state.config`.
- At shutdown, record `"close"`.
- `GET /currency` answers `{"currency": "INR"}`, reading the value from the state.

**Step 1.** A module-level list to watch what happens.

```python
LOG = []
```

**Step 2.** The lifespan. Startup before `yield`, shutdown after.

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    LOG.append("open")
    app.state.config = {"currency": "INR"}
    yield
    LOG.append("close")
```

**Step 3.** The app and the route.

```python
app = FastAPI(lifespan=lifespan)

@app.get("/currency")
def currency(request: Request):
    return {"currency": request.app.state.config["currency"]}
```

**Step 4.** Test it. Use `with`, and look at `LOG` before, during and after.

```python
print(LOG)                              # -> []
with TestClient(app) as client:
    print(LOG)                          # -> ['open']
    print(client.get("/currency").json())   # -> {'currency': 'INR'}
print(LOG)                              # -> ['open', 'close']
```

## A shared HTTP client (the real use)

In lesson 12 you saw that you should create **one** `httpx.AsyncClient` and reuse it, because it keeps connections open. The lifespan is the right place:

```python
import httpx

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http = httpx.AsyncClient(timeout=5.0)
    yield
    await app.state.http.aclose()          # close connections cleanly

app = FastAPI(lifespan=lifespan)

@app.get("/ip")
async def my_ip(request: Request):
    r = await request.app.state.http.get("https://api.ipify.org?format=json")
    return r.json()
```

The same shape fits other long-lived things:

- a database **engine** (create at startup, `dispose()` at shutdown),
- a Redis connection pool,
- a machine-learning or embedding model (loading takes seconds, so do it once),
- a background task that runs while the app runs.

If a startup step fails, the app does not start. This is good: the server fails **fast** at deploy time and not on the first user request.

To hand the shared object to routes in a clean way, wrap `request.app.state.http` in a small dependency (lesson 8), so tests can override it with a fake:

```python
def get_http(request: Request) -> httpx.AsyncClient:
    return request.app.state.http
```

## Mounting a sub-app

`app.mount(path, other_app)` serves a **whole separate app** under a path. The sub-app has its own routes, its own docs and its own middleware.

```python
admin = FastAPI()

@admin.get("/stats")
def stats():
    return {"admin": True}

app = FastAPI()
app.mount("/admin", admin)

print(TestClient(app).get("/admin/stats").json())   # -> {'admin': True}
```

The URL is `/admin/stats`. The sub-app's docs are at `/admin/docs`.

When to use it: to attach a different app (an admin panel, a static files folder, an old version of an API). To split **one** API into several files, do not mount. Use `APIRouter` and `include_router` (lesson 6).

Static files are a typical mount: `app.mount("/static", StaticFiles(directory="static"), name="static")` (from `fastapi.staticfiles`).

## Compression and host checks

Two small middleware (lesson 13 explained what middleware is) that real apps add:

```python
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["api.example.com", "testserver"])

@app.get("/big")
def big():
    return {"data": "x" * 2000}

client = TestClient(app)
r = client.get("/big", headers={"Accept-Encoding": "gzip"})
print(r.headers["content-encoding"])                         # -> gzip
print(client.get("/big", headers={"Host": "evil.com"}).status_code)   # -> 400
```

- **GZip** compresses big answers when the client says it understands gzip (`Accept-Encoding: gzip`). JSON compresses very well, so a big list can become 5 to 10 times smaller. `minimum_size` skips tiny answers, where compressing costs more than it saves.
- **TrustedHost** checks the `Host` header, and answers `400` for a host that is not in your list. This blocks "host header" tricks, where a request pretends to be for another domain.
- In production, a reverse proxy (Nginx, a load balancer) often does compression and host checks. Do it in the app when you have no proxy in front, or you want the same rules everywhere.

## Shaping the API docs

FastAPI builds the docs (`/docs`) from your code, using an **OpenAPI** schema at `/openapi.json`. OpenAPI is a standard description of an API. Tools can read it to draw docs, make a typed client in another language, or test the API.

Set the basics when you create the app:

```python
app = FastAPI(
    title="Shop API",
    version="2.1.0",
    description="Small shop backend",
    openapi_tags=[{"name": "items", "description": "Item operations"}],
)
```

Then give each route a bit of metadata:

```python
@app.get("/items", tags=["items"], summary="List items", operation_id="list_items")
def list_items():
    return [{"id": 1}]

@app.get("/items/old", tags=["items"], deprecated=True)
def list_items_old():
    return [{"id": 1}]

@app.get("/internal", include_in_schema=False)
def internal():
    return {"secret": True}
```

- `tags` groups routes on the docs page (`openapi_tags` adds a description for each group).
- `summary` is the short title. The function's docstring becomes the long description.
- `operation_id` is a stable name for the route. Code generators use it to name client functions, so `list_items` becomes a function `listItems()`.
- `deprecated=True` shows the route as old. It still works. Pair it with the `Deprecation` header from lesson 14.
- `include_in_schema=False` hides the route from the docs. It still works, so it is **not** a security tool.
- `docs_url`, `redoc_url` and `openapi_url` can be changed, or set to `None` to switch the docs off (a common choice in production for private APIs).

You can read the schema from Python with `app.openapi()`. It returns a dict, so you can test it:

```python
schema = app.openapi()
print(schema["info"]["title"])                      # -> Shop API
print("/internal" in schema["paths"])               # -> False
print(schema["paths"]["/items/old"]["get"]["deprecated"])   # -> True
```

You can also document extra answers: `responses={404: {"description": "Item not found"}}` on the decorator. Good docs save your teammates (and the frontend team) many questions.

## Backend concept: the process lifecycle in production

A real server does not just "run". Think about what happens at deploy time:

1. The platform starts a new copy of your app.
2. **Startup** runs. The app connects to the database and warms up.
3. A health check tells the platform when it is ready (Level 3).
4. Traffic arrives.
5. On a new deploy, the platform sends the **stop** signal (`SIGTERM`). The app finishes the requests in progress, then the **shutdown** code runs. Then the process ends.

Lifespan is your hook into steps 2 and 5. Closing connections cleanly on shutdown avoids broken requests and leaked connections during a deploy.

## A little deeper (optional)

- **Sub-app lifespans.** A mounted sub-app does not run its own lifespan by default. Put shared resources in the **main** app's lifespan.
- **Slow startup.** If loading a model takes 30 seconds, the platform must wait. A readiness check (Level 3) tells it when you are ready.
- **`app.state` and several workers.** Each worker process runs its own lifespan and has its own `app.state`. Do not store data that must be shared (like a counter) there. Use a database or Redis for that.
- **Customising the schema.** You can write your own function that edits `app.openapi()` and cache the result. It is rarely needed.
- **ReDoc.** `/redoc` is a second, read-only docs page.

## Common mistakes

- Testing a route that needs `app.state` without `with TestClient(app)`.
- Creating a new `httpx.AsyncClient` (or database engine) for every request.
- Forgetting to close what you opened, after `yield`.
- Using `include_in_schema=False` as protection. Hidden is not secret.
- Storing data that many workers must share in `app.state`.
- Mounting a sub-app when an `APIRouter` was what you wanted.
- Compressing tiny answers. Set `minimum_size`.

## Interview corner

- **Q: How do you run code at startup and shutdown in FastAPI?** Pass a `lifespan` async context manager to `FastAPI(lifespan=...)`. Code before `yield` is startup, code after is shutdown. `on_event` is deprecated.
- **Q: Where do you create the database engine or an HTTP client?** In the lifespan (or once at module level for the engine), keep it in `app.state`, and close it after `yield`. Hand it out through a dependency.
- **Q: Dependency with `yield` versus lifespan?** A dependency runs for each request. A lifespan runs once for the app.
- **Q: How do you make API docs better?** Titles, tags, summaries, descriptions, response examples, `operation_id`, and `deprecated` for old routes.
- **Q: What happens to in-flight requests when you deploy?** The platform sends `SIGTERM`. The server stops taking new requests and finishes the current ones, then the shutdown code runs.

## Summary

- `lifespan`: one `yield`. Before it is startup, after it is shutdown. Replace `on_event`.
- Keep long-lived objects in `app.state`, read them with `request.app.state`, and wrap them in a dependency.
- `TestClient` runs the lifespan only inside `with`.
- `app.mount(path, other_app)` serves a separate app under a path. For splitting your own API, use `APIRouter`.
- `GZipMiddleware` (with `minimum_size`) and `TrustedHostMiddleware` are small, useful middleware.
- `tags`, `summary`, `operation_id`, `deprecated` and `include_in_schema` shape the OpenAPI docs. `app.openapi()` is a dict you can test.
