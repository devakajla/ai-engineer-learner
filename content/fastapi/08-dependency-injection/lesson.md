---
title: Dependency injection
summary: Let FastAPI build the things your routes need (settings, services, database sessions, the current user) and swap them in tests.
plan_ids: [FA-02, SD-01]
---

In lesson 6, `tasks.py` made its service at the top of the file, like this: `task_service = TaskService(InMemoryTaskRepository(...))`. It works, but it is **hard-wired**. A test cannot swap the storage. And every request shares that one object, whether you want it or not.

**Dependency injection** (DI) fixes this. FastAPI has it built in, with a tool called `Depends`.

## The idea in plain words

A **dependency** is something a function needs in order to work. For a route, it might be a service, a settings object, or a database connection.

There are two ways to get it:

- The function **builds** it itself. This is hard-wired.
- The function **asks** for it, and somebody else gives it. This is **injection**.

```python
# hard-wired: the function creates what it needs
def list_tasks():
    service = TaskService(InMemoryTaskRepository())
    ...

# injected: the function declares what it needs, and receives it
def list_tasks(service: TaskService = Depends(get_task_service)):
    ...
```

Why it is good:

- You can swap one thing for another (memory storage for a database).
- In tests you can give a fake.
- Shared set-up (login check, paging, database sessions) is written once and reused.
- Routes stay short.

## `Depends` basics

A dependency is **any function** (any "callable"). For each request, FastAPI calls it for you. FastAPI also fills in the dependency's own parameters, the same way it does for a route: from the query, the path, headers, or other dependencies.

```python
from typing import Annotated
from fastapi import Depends, Query

def pagination(
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    return {"limit": limit, "offset": offset}

@app.get("/tasks")
def list_tasks(page: Annotated[dict, Depends(pagination)]):
    return page
```

```text
GET /tasks?limit=5   -> {"limit": 5, "offset": 0}
GET /tasks?limit=0   -> 422
```

Look at the pieces:

- `Depends(pagination)` means: "call `pagination` and give me its result".
- Pass the **function itself**, not its result. Write `Depends(pagination)`, never `Depends(pagination())`.
- The `limit` and `offset` rules are written once. Every route that uses this dependency gets them.

To reuse it, give the whole type a short name (an **alias**):

```python
Pagination = Annotated[dict, Depends(pagination)]

@app.get("/tasks")
def list_tasks(page: Pagination): ...

@app.get("/users")
def list_users(page: Pagination): ...     # same rules, no copy-paste
```

## Worked example: one dependency, two routes

Exercise 1 asks for a pagination dependency, used in two routes. Here is the same pattern for a different problem: a **search** dependency with a text `q` and a number `top`.

Goal: two routes (`/fruits` and `/colors`) that both accept `?q=...&top=...`.

**Step 1.** Choose what the dependency returns. A small `dataclass` is a neat container (you saw dataclasses in Python lesson 20).

```python
from dataclasses import dataclass

@dataclass
class Search:
    q: str
    top: int
```

**Step 2.** Write the dependency. Its parameters become query parameters, and the rules go here.

```python
def search_params(
    q: Annotated[str, Query(max_length=20)] = "",
    top: Annotated[int, Query(ge=1, le=10)] = 3,
) -> Search:
    return Search(q=q, top=top)
```

**Step 3.** Make the alias.

```python
SearchDep = Annotated[Search, Depends(search_params)]
```

**Step 4.** Use the alias in both routes.

```python
FRUITS = ["apple", "banana", "mango", "melon"]
COLORS = ["red", "blue", "green"]

@app.get("/fruits")
def fruits(s: SearchDep):
    found = [f for f in FRUITS if s.q in f]
    return found[: s.top]

@app.get("/colors")
def colors(s: SearchDep):
    found = [c for c in COLORS if s.q in c]
    return found[: s.top]
```

**Step 5.** Check it.

```python
client = TestClient(app)
print(client.get("/fruits?q=m&top=2").json())   # -> ['mango', 'melon']
print(client.get("/colors?top=0").status_code)  # -> 422
```

Both routes reject a bad `top`, and the rule exists in only one place.

## Dependency chains

A dependency can have its own dependencies. FastAPI builds the whole chain for you.

```python
from functools import lru_cache

@lru_cache
def get_settings() -> Settings:
    return Settings()

def get_task_repository() -> TaskRepository:
    return _repository                 # one shared store, for now

def get_task_service(
    repo: Annotated[TaskRepository, Depends(get_task_repository)],
) -> TaskService:
    return TaskService(repo)

TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]

@router.get("")
def list_tasks(service: TaskServiceDep): ...
```

When a request comes in, FastAPI calls `get_task_repository`, passes the result to `get_task_service`, and passes that result to your route.

Inside **one request**, each dependency runs **only once**. If two parts need the same dependency, they share the one result. (This is the default and is called caching.)

## `yield` dependencies: set up, then clean up

Some things must be closed after use: a database session, a file, a network client. Use `yield` instead of `return`:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db          # the route runs now, with this db
    finally:
        db.close()        # runs after the response is sent, even if there was an error
```

The code before `yield` is the set-up. The code after `yield` is the clean-up. This is a context manager in disguise (you met these in Python lesson 24). You will use exactly this in the SQLAlchemy lesson.

## Dependencies that guard a route

A dependency can **reject** a request by raising an error. This is how login checks and API keys work.

```python
from fastapi import Header, HTTPException, status

def require_api_key(x_api_key: Annotated[str | None, Header()] = None) -> str:
    if x_api_key != settings.api_key:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid API key")
    return x_api_key
```

- `Header()` reads a request header. The parameter name `x_api_key` maps to the header `X-API-Key`: underscores become hyphens, and case does not matter.
- To guard **one route** without using the value, put the dependency in the decorator: `@router.post("", dependencies=[Depends(require_api_key)])`.
- To guard a **whole router**: `APIRouter(dependencies=[Depends(require_api_key)])`.

## Replace a dependency in tests

This is the best part of DI. In a test you can tell the app: "when someone asks for `get_task_service`, give them this instead".

```python
def test_list_is_empty():
    app.dependency_overrides[get_task_service] = lambda: TaskService(InMemoryTaskRepository())
    try:
        assert client.get("/api/v1/tasks").json() == []
    finally:
        app.dependency_overrides.clear()
```

- `app.dependency_overrides` is a dictionary: original function → replacement function.
- Always call `.clear()` afterwards, so one test does not leak into the next.
- No patching and no global tricks are needed. Real projects use this for test databases, fake email senders and fake AI clients.

Here is the pattern on a tiny example, a "clock" dependency:

```python
def get_clock():
    return "real time"

@app.get("/now")
def now(clock: Annotated[str, Depends(get_clock)]):
    return {"now": clock}

app.dependency_overrides[get_clock] = lambda: "fake time"
print(TestClient(app).get("/now").json())   # -> {'now': 'fake time'}
app.dependency_overrides.clear()
```

## Settings with `lru_cache`

```python
from functools import lru_cache

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

`@lru_cache` remembers the result of the function. So the environment is read **once**, and every later call gives back the same object. Because code asks for settings through a function, a test can still replace it with `dependency_overrides`, or call `get_settings.cache_clear()`.

## Backend concept: inversion of control

In old-style code, a high-level part creates its own low-level parts. A `TaskService` builds its own repository.

With **inversion of control**, the order flips. Something outside (the framework, or `main.py`) builds the parts and **passes them in**. The service just uses what it receives.

This is the "D" in the famous SOLID rules: *depend on a simple contract, and let someone else supply the real thing*. FastAPI's `Depends` is a small DI system driven by type hints.

## A little deeper (optional)

- **Classes as dependencies.** A class is also callable, so `Depends(MyClass)` works: FastAPI calls `MyClass(...)` and fills its `__init__` parameters. It is handy for bundling several query parameters:

  ```python
  class TaskFilters:
      def __init__(self, done: bool | None = None, q: str | None = None):
          self.done = done
          self.q = q

  @router.get("")
  def list_tasks(filters: Annotated[TaskFilters, Depends()]): ...
  ```

  `Depends()` with nothing inside means "use the type hint as the callable".
- **`use_cache=False`.** If you really want a dependency to run again within the same request, write `Depends(fn, use_cache=False)`.
- **Factory function.** The `create_app()` function in the project step builds a fresh app each time it is called. Tests and workers can use it to get a clean, fully set-up app.

## Common mistakes

- Calling the function yourself: `Depends(get_db())`. Pass the function, do not call it.
- Creating expensive objects (a database engine, an HTTP client) inside a per-request dependency. Create them **once** and give out only a cheap per-request handle.
- Forgetting `app.dependency_overrides.clear()` after a test. The override then leaks into other tests.
- Putting business rules inside dependencies. A dependency should **provide** something or **guard** a route. Rules belong in services.

## Interview corner

- **Q: What is dependency injection, and why use it?** A part receives what it needs instead of creating it. This lets you swap implementations, test with fakes, and reuse shared logic.
- **Q: How do you test a FastAPI route without the real database?** Use `app.dependency_overrides[get_db] = some_function_that_returns_a_test_session`.
- **Q: A dependency is needed by two sub-dependencies in one request. How many times does it run?** Once. The result is cached for that request, unless you pass `use_cache=False`.
- **Q: How do `yield` dependencies work?** Code before `yield` runs before the route. The yielded value is injected. Code after `yield` runs after the response. It is ideal for database sessions.

## Summary

- `Depends(function)` asks FastAPI to call the function and inject the result. Reuse it with an `Annotated[T, Depends(fn)]` alias.
- Dependencies can depend on other dependencies. Each runs once per request.
- `yield` gives set-up and clean-up. Raising inside a dependency rejects the request.
- `dependencies=[...]` on a route or router adds guards such as an API key.
- `app.dependency_overrides` swaps a dependency in tests. `@lru_cache` makes settings load once.
