---
title: Project structure & config
summary: Split a growing app into routers, services and repositories, and read settings from the environment.
plan_ids: [FA-08, SD-01]
---

Right now TaskFlow's `main.py` does everything: it handles HTTP, applies the business rules, and stores the data. For a 50-line file that is fine. For a 5,000-line project it is painful.

In this lesson you learn the folder structure that most real FastAPI projects use, and the **reason** behind each part. Interviewers like to ask about those reasons.

## Why one big file hurts

- To change where data is stored (a list today, a database later), you must edit your route functions.
- You cannot test a business rule without making an HTTP call.
- Two people editing the same `main.py` keep clashing.
- Settings (a debug flag, a database address, secrets) end up typed directly in the code.

## Layers: each part has one job

We split the code by **responsibility**. Each layer talks only to the layer below it.

```
HTTP request
   |
   v
routes        (app/api/routes/)     HTTP only: read the input, call the service, choose the status code
   |
   v
services      (app/services/)       business rules: "a title must be unique", ...
   |
   v
repositories  (app/repositories/)   storage only: get, add, update, delete
   |
   v
data          (memory today, a database later)
```

Two more folders sit beside them:

- `schemas/`: the Pydantic models (the shapes of requests and responses).
- `core/`: settings and other set-up that many parts share.

Why this helps:

- Each file has **one reason to change**.
- You can **swap the storage** by writing a new repository. Routes and services stay the same.
- You can **test the rules** by calling the service directly, with no HTTP.
- Code only points **downward**. A repository never imports a route.

> Not every app needs every layer. A tiny app can go routes straight to storage. Add a service layer when real business rules appear. The skill is knowing why each layer exists.

## The folder structure we will use

```
taskflow/
├── app/
│   ├── __init__.py
│   ├── main.py                  # create the app, include routers, nothing else
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py            # settings
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── health.py
│   │       └── tasks.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── task.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_service.py
│   └── repositories/
│       ├── __init__.py
│       └── task_repository.py
├── tests/
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

## `APIRouter`: routes in their own file

Until now every route was on `app`. An **`APIRouter`** is a small "mini app" that holds the routes of one topic. You write it in its own file, then plug it into the main app.

```python
# app/api/routes/pets.py
from fastapi import APIRouter

router = APIRouter(prefix="/pets", tags=["pets"])

@router.get("")                  # full path: /pets
def list_pets():
    return []

@router.get("/{pet_id}")         # full path: /pets/{pet_id}
def get_pet(pet_id: int):
    return {"id": pet_id}
```

```python
# app/main.py
from fastapi import FastAPI
from app.api.routes import pets

app = FastAPI()
app.include_router(pets.router, prefix="/api/v1")   # paths become /api/v1/pets ...
```

- `prefix` and `tags` are written **once on the router**, not on every route.
- Use `""` (empty text) for the collection route. The router's prefix already gives `/pets`.
- Prefixes **stack from the outside in**: the `include_router` prefix, then the router prefix, then the route path. So `GET /{pet_id}` becomes `/api/v1/pets/{pet_id}`.
- This also **versions** the API. Later, if you need breaking changes, you can add `/api/v2` next to `/api/v1`.

## Worked example: a router under `/api/v1`

Exercise 1 asks for a router with a prefix and a tag, included under `/api/v1`. Here is the same pattern for a different problem: **pets**.

Goal:

```text
GET /api/v1/pets      -> []
GET /api/v1/pets/3    -> {"id": 3}
GET /pets             -> 404   (only the versioned path exists)
```

**Step 1.** Create the router. Put the prefix and the tag on the router itself.

```python
router = APIRouter(prefix="/pets", tags=["pets"])
```

**Step 2.** Add the routes. Their paths are relative to the prefix.

```python
@router.get("")
def list_pets():
    return []

@router.get("/{pet_id}")
def get_pet(pet_id: int):
    return {"id": pet_id}
```

**Step 3.** Create the app and include the router with the version prefix.

```python
app = FastAPI()
app.include_router(router, prefix="/api/v1")
```

**Step 4.** Check each line of the goal.

```python
client = TestClient(app)
print(client.get("/api/v1/pets").json())       # -> []
print(client.get("/api/v1/pets/3").json())     # -> {'id': 3}
print(client.get("/pets").status_code)         # -> 404
```

## Settings from the environment

Some values change between your laptop, a test server and the real server: a debug flag, a database address, a secret key. These are called **settings** (or *config*).

A well-known rule (the **12-factor app**): settings live in **environment variables**, not in the code.

An **environment variable** is a named value that your operating system gives to a program, like `DEBUG=true`.

The library `pydantic-settings` reads them for you and checks their types, just like a Pydantic model.

```bash
uv add pydantic-settings
```

```python
# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "TaskFlow"
    debug: bool = False
    max_page_size: int = 50

settings = Settings()
```

How it works:

- Each field reads the environment variable with the **same name**, ignoring upper or lower case. `DEBUG=true` makes `settings.debug` equal `True`.
- The value is **converted and checked**. `MAX_PAGE_SIZE=abc` raises a validation error when the app starts. That is good: you find the mistake at once.
- `env_file=".env"` also reads a local file named `.env`. **Never commit that file**, because it holds secrets.
- Commit a file named **`.env.example`** instead. It lists every variable with a safe placeholder value, so teammates know what to set.

The order of priority, from strongest to weakest: **real environment variables**, then the **`.env` file**, then the **defaults** in the class.

```python
import os
os.environ["APP_NAME"] = "Demo"
print(Settings().app_name)   # -> Demo
```

Create the settings object when you need it (`Settings()`), and it reads the environment at that moment.

## The service and the repository

A **repository** is a class that only stores and fetches data. A **service** is a class that holds the business rules, and uses a repository.

Here is a small example with **coupons**:

```python
# repository: storage only
class CouponRepository:
    def __init__(self):
        self._items = {}

    def get(self, code):
        return self._items.get(code)

    def add(self, code, percent):
        self._items[code] = {"code": code, "percent": percent}
        return self._items[code]
```

```python
# service: rules only
class CouponNotFoundError(Exception):
    pass

class CouponService:
    def __init__(self, repo):
        self.repo = repo

    def get(self, code):
        coupon = self.repo.get(code)
        if coupon is None:
            raise CouponNotFoundError(code)
        return coupon
```

Look closely: the service raises its **own error**, `CouponNotFoundError`. It does **not** raise `HTTPException`. A service should know nothing about HTTP. The same service might be used later by a script or a background job, where "404" means nothing.

The **route** is the layer that knows HTTP. It translates the service's error into a status code:

```python
service = CouponService(CouponRepository())

@router.get("/{code}")
def get_coupon(code: str):
    try:
        return service.get(code)
    except CouponNotFoundError:
        raise HTTPException(status_code=404, detail="Coupon not found")
```

An error that belongs to your business ("coupon not found") is called a **domain error**. (In lesson 8 you will replace the module-level `service = ...` with *dependency injection*. In lesson 13 you will remove the `try/except` from routes with global handlers.)

A rule can also live in the service. For example, "a coupon code must be unique": inside `add`, the service checks whether the code exists, and raises a `DuplicateCouponError` if it does. The route turns that into `409`.

## Backend concept: cohesion and coupling

- **Cohesion**: things that change together live together. All task routes are in `tasks.py`.
- **Coupling**: how much one part depends on the inside details of another. Low coupling means you can change one part without breaking the others.

Layers plus small, clear interfaces give high cohesion and low coupling. That is the whole goal of "clean architecture".

## A little deeper (optional)

- `main.py` should stay tiny: create the app and include routers. All the real work lives elsewhere.
- Files named `__init__.py` make a folder a **package**, so you can write `from app.core.config import settings`.
- Creating `settings = Settings()` at module level is simple. Later (lesson 8) you will cache it with `@lru_cache` and give it to routes with dependency injection.
- A service can be tested alone: `CouponService(CouponRepository()).get("x")` needs no server.

## Common mistakes

- Putting business logic in route functions ("fat routes").
- A service that raises `HTTPException`. Now it is stuck to HTTP.
- Hard-coding secrets or addresses in code, or committing `.env`.
- **Circular imports**: for example a repository that imports a route, and the route imports the repository. Keep imports pointing downward.
- Over-building. A 3-endpoint app does not need five layers. Match the structure to the size.

## Interview corner

- **Q: How do you structure a FastAPI project, and why?** Routers per resource, schemas for shapes, services for business rules, repositories for storage, core for settings. The reasons are separation of concerns, easy testing, and the ability to swap storage.
- **Q: Where do you keep settings and secrets?** In environment variables, read with pydantic-settings. Locally in a `.env` file that is not committed. A `.env.example` documents the names. In production, a secrets manager.
- **Q: Why should a service not raise `HTTPException`?** It ties business logic to HTTP. The service may be called from a worker or a script. Raise domain errors and translate them at the edge (the route).

## Summary

- Routes (HTTP) call services (rules), which call repositories (storage). Code points downward.
- `APIRouter(prefix, tags)` per topic. `include_router(prefix="/api/v1")` adds the version.
- Settings come from environment variables via `pydantic-settings`. Commit `.env.example`, never `.env`.
- Services raise domain errors. Routes turn them into status codes.
