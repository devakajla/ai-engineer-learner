---
title: Your first FastAPI app
summary: Run a real API server, write your first routes, and use the free interactive docs and TestClient.
plan_ids: [FA-01]
---

In this lesson you build and run a real API. You will also see what sits between a request from `curl` and your Python function, so nothing feels like magic.

## Who does what?

A request passes through three layers before it reaches your code:

```
client (curl or browser)
     |   HTTP request
     v
uvicorn    -> the web server: listens on a port, reads the raw HTTP text
     |
     v
FastAPI    -> the framework: finds the right route, checks the data, makes the JSON
     |
     v
your function -> returns a dict
```

- **uvicorn** is the **server**. It waits on a port (like `8000`), receives the HTTP text, and hands it to FastAPI.
- **FastAPI** is the **framework**. It does the boring work for you: routing (which function for which URL), checking data, and building responses.
- **Your function** is the part you write.

Two more names you will hear:

- **ASGI** is the agreement (a set of rules) between a server like uvicorn and a framework like FastAPI. It lets them work together. It supports `async` code, streaming and WebSockets. (Its older cousin, **WSGI**, does not.)
- FastAPI is built from two libraries: **Starlette** (the web toolkit) and **Pydantic** (checks data; you will use it in lesson 4).

> **Interview line:** "FastAPI is an ASGI framework built on Starlette and Pydantic. Uvicorn is the ASGI server that runs it."

## Hello, API

Here is a complete app:

```python
# app/main.py
from fastapi import FastAPI

app = FastAPI(title="TaskFlow", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok"}
```

Line by line:

- `app = FastAPI(...)` creates the **application object**. This one object is your whole API.
- `@app.get("/health")` is a **decorator**. A decorator is a line placed above a function that adds something to it. Here it says: "when a `GET` request comes to `/health`, call the function below". This pair (a method and a path, linked to a function) is called a **route**, or a *path operation*.
- The function returns a `dict`. FastAPI turns it into JSON and sets the header `Content-Type: application/json` for you.

## Run it

```bash
uv run fastapi dev app/main.py
```

`fastapi dev` starts the server in **development mode**. It restarts by itself every time you save a file.

There is another way, where you call uvicorn yourself:

```bash
uv run uvicorn app.main:app --reload --port 8000
```

Look at `app.main:app`. The part before the colon is the **module** to import (`app/main.py`, written as `app.main`). The part after the colon is the **variable** inside it (`app`). So it means: "import `app.main` and use the thing named `app`".

Now call your API from a second terminal:

```bash
curl -i localhost:8000/health
# -> HTTP/1.1 200 OK
# -> content-type: application/json
# ->
# -> {"status":"ok"}
```

(`curl -i` also prints the status line and headers. You learned these in lesson 1.)

> `--reload` is only for development. Do not use it in production.

## Free interactive docs

FastAPI reads your routes and builds documentation by itself. Open these in a browser:

| URL | What you get |
|---|---|
| `/docs` | **Swagger UI**: a page where you can click and try every endpoint |
| `/redoc` | a clean, read-only version of the docs |
| `/openapi.json` | the same information as raw data, for programs |

The `title`, `version` and `description` you give to `FastAPI(...)` show up in these docs.

```python
app = FastAPI(title="Notes", version="1.0.0", description="A tiny notes API")
```

Because `app` is an object, you can read those values back later: `app.title` is `"Notes"` and `app.version` is `"1.0.0"`. That way you never need to type the same text twice.

## One path, many methods

Each method has its own decorator: `@app.get`, `@app.post`, `@app.put`, `@app.patch`, `@app.delete`.

```python
@app.get("/notes")
def list_notes():
    return []

@app.post("/notes")
def create_note():
    return {"created": True}
```

The same path with different methods gives different functions.

What if a client uses a method you did not write?

- Path exists, but not for that method: FastAPI answers **`405 Method Not Allowed`**.
- Path does not exist at all: FastAPI answers **`404 Not Found`**.

You get both for free.

## Testing without a server: `TestClient`

In tests you do not need to start uvicorn. FastAPI gives you `TestClient`, which sends a fake request straight into your app, all inside Python.

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

response = client.get("/health")
print(response.status_code)   # -> 200
print(response.json())        # -> {'status': 'ok'}
```

- `client.get(...)`, `client.post(...)`, `client.delete(...)` exist for every method.
- `response.status_code` is the number. `response.json()` turns the JSON body into a Python object.

This is how the app checks your exercises and your project.

## Worked example: a route and its test

Exercise 1 asks you to make an app with a route that returns a message. Here is the same pattern for a different problem: a route `GET /ping` that returns `{"pong": true}`.

**Step 1.** Import `FastAPI` and create the `app` variable.

```python
from fastapi import FastAPI

app = FastAPI()
```

**Step 2.** Write a function that returns the data, and put the decorator above it with the method and path.

```python
@app.get("/ping")
def ping():
    return {"pong": True}
```

Python's `True` becomes JSON `true` automatically.

**Step 3.** Check it with `TestClient`.

```python
from fastapi.testclient import TestClient

client = TestClient(app)
response = client.get("/ping")
print(response.status_code)   # -> 200
print(response.json())        # -> {'pong': True}
```

That is the whole recipe: **create `app`, add a decorated function, return data**.

The tests for your exercises import the variable named `app`, so keep that exact name.

## `def` or `async def`?

Both work in FastAPI:

```python
@app.get("/a")
def a():
    return {"a": 1}

@app.get("/b")
async def b():
    return {"b": 1}
```

For now: **use plain `def`**. Use `async def` only when you `await` something inside. Lesson 12 explains why, in detail.

## Backend concept: ports and processes

A server is a **program that keeps running and listens on a port**. A port is like a door number on your computer. Only one program can use a given port at a time.

- If you see `Address already in use`, another program already has that port. Stop it, or pick another port with `--port 8001`.
- By default the server accepts connections only from your own computer (`127.0.0.1`). The setting `--host 0.0.0.0` means "accept from anywhere". You need it inside Docker (lesson 23).
- In production, people run **many copies** of the app at the same time, behind a load balancer. Each copy is its own process. This is a big reason an API should be **stateless**: you cannot be sure which copy gets your next request.

## A little deeper (optional)

- `tags=["health"]` inside a decorator groups the route in `/docs`. A docstring (the text in triple quotes at the top of a function) is shown there as the description.
- A **return type hint** such as `-> dict[str, str]` documents what the route returns. It helps your editor and your docs.
- With `async def`, FastAPI runs your function directly. With plain `def`, FastAPI runs it in a separate thread so it cannot block other requests.

```python
@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    """Check that the server is alive."""
    return {"status": "ok"}
```

## Common mistakes

- Running `uvicorn main:app` from the wrong folder gives `Could not import module`. The text must match your real file path (for example `app.main:app`).
- Writing `@app.route(...)`. That is Flask. In FastAPI use `@app.get`, `@app.post`, and so on.
- Naming the variable something other than `app`, so the tests and the server cannot find it.
- Returning something FastAPI cannot turn into JSON, like a plain custom class object. This gives a `500` error.

## Summary

- uvicorn (server) hands the request to FastAPI (framework), which calls your function.
- `@app.get(path)` (and `post`, `delete`, ...) creates a route. A returned dict becomes JSON.
- `/docs`, `/redoc` and `/openapi.json` are free. Set `title`, `version` and `description` on `FastAPI(...)`; read them back with `app.title` and `app.version`.
- Wrong method on a known path is `405`; unknown path is `404`.
- `TestClient(app)` calls your API in tests, without a running server.
- Use `def` unless you need `await`.
