# 2. Your first FastAPI app

FastAPI is a Python tool for building web APIs. You write normal Python functions, and FastAPI turns them into URLs. It also checks the data for you, and makes a free documentation page.

## Idea: a function becomes a URL

You write:

```python
@app.get("/health")
def health():
    return {"status": "ok"}
```

Read it as: *"When someone sends `GET /health`, run this function and send back what it returns as JSON."*

## Steps

::: {.step}
Step 1: create the project folder
:::

```bash
mkdir taskflow
cd taskflow
uv init --bare
```

`uv init --bare` creates one file, `pyproject.toml`. It is the "ID card" of your project: name, Python version, and later the list of packages.

::: {.step}
Step 2: add FastAPI
:::

```bash
uv add "fastapi[standard]"
```

This does three things: creates a private environment in `.venv/`, installs FastAPI and its tools (`[standard]` includes the `fastapi` command and the Uvicorn server), and records them in `pyproject.toml`. You never need to "activate" anything. You just put `uv run` in front of commands.

::: {.step}
Step 3: create the app package
:::

```bash
mkdir app
touch app/__init__.py
```

The empty `__init__.py` file tells Python "this folder is a package". Then other files can write `from app.something import ...`. We start with `app/` from day one, even though we only have one file, because every real project does, and it saves a messy move later.

::: {.step}
Step 4: write `app/main.py`
:::

```python
from fastapi import FastAPI

app = FastAPI(title="TaskFlow")


@app.get("/health")
def health():
    return {"status": "ok"}
```

- `FastAPI(...)` creates the application object. Its name is `app` by convention.
- `@app.get("/health")` is a **decorator**. It registers the function below it for `GET /health`.
- The function returns a normal Python `dict`. FastAPI converts it to JSON.

::: {.step}
Step 5: run it
:::

```bash
uv run fastapi dev app/main.py
```

You will see:

```
 Starting FastAPI in development mode
 Using import string: app.main:app
 Server started at http://127.0.0.1:8000
    Documentation at http://127.0.0.1:8000/docs
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

`app.main:app` means "in the file `app/main.py`, take the variable `app`". `dev` mode **reloads automatically** when you save a file. Leave it running and use a second terminal for the next commands.

::: {.step}
Step 6: call it
:::

```bash
curl localhost:8000/health
# -> {"status":"ok"}
```

Now open `http://127.0.0.1:8000/docs` in your browser. FastAPI made an interactive page for you. Click `GET /health`, then "Try it out", then "Execute". You can test any endpoint here without curl.

::: {.step}
Step 7: save your work with git
:::

```bash
git init
printf ".venv/\n__pycache__/\n.env\n*.db\n" > .gitignore
git add . && git commit -m "first FastAPI app"
```

The `.gitignore` file lists things git must never save: the environment, caches, the `.env` file with secrets, and local databases.

::: {.box .checkpoint}
**Folder now**

```
taskflow/
├── .gitignore
├── pyproject.toml
├── uv.lock               # exact versions installed (made by uv)
└── app/
    ├── __init__.py
    └── main.py
```

**Checkpoint:** `curl localhost:8000/health` prints `{"status":"ok"}` and `/docs` opens in the browser.
:::

## What happens when you run it

@@ flow | Figure 2.1: the pieces that run your code.
Uvicorn|the web server;speaks HTTP|blue -> FastAPI|finds the route;checks the data|green -> Your function|runs your code|yellow
@@ end

Uvicorn waits for connections. FastAPI picks the function that matches the method and path. Your function does the work. FastAPI turns the result into a response. You only write the yellow part.

## The free documentation

FastAPI reads your code and builds an **OpenAPI** description of the API at `/openapi.json`. The pages `/docs` (Swagger UI) and `/redoc` are drawn from it. When you change your code, the docs change too, so they are never out of date.

## `def` or `async def`?

You can write `def health()` or `async def health()`. Both work. For now use plain `def`. Chapter 9 explains `async` and when it matters. A short rule for later: use `async def` only if everything you call inside is also awaited with `await`.

::: {.box .why}
**Why `app/main.py` and not `main.py`?**

A package named `app` gives every file a stable address: `app.main`, `app.core.config`. Imports always start from `app`, so they work the same from tests, from Docker and from the command line.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Running `fastapi dev main.py` when your file is `app/main.py`. Use the right path.
- Forgetting `uv run`. Without it you use the wrong Python and see `ModuleNotFoundError`.
- Forgetting `__init__.py`. Imports may fail in strange ways.
- Using `fastapi dev` for production. It reloads on every change and is only for development.
- Committing the `.venv` folder or `.env` to git.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: What is FastAPI built on?**
Starlette (web parts) and Pydantic (data validation). Uvicorn is the server that runs it.

**Q: How do you get API documentation?**
It is automatic. FastAPI builds an OpenAPI schema from your code and serves it at `/docs` and `/redoc`.

**Q: What does `app.main:app` mean?**
Import the variable `app` from the module `app.main`.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Add `GET /hello` that returns `{"message": "Hello, FastAPI"}`. Check it in `/docs`.
2. Add `GET /version` that returns `{"version": "1.0.0"}`.
3. Stop the server with `Ctrl+C`, run `uv run python -c "import fastapi; print(fastapi.__version__)"` and write the version down.
4. Add a second route with the **same path** and method. Which one runs? Test it.
5. **Think:** why does the dev server reload by itself, and why must production not do that?
:::
