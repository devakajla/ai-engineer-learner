# 15. Testing your API

A test is a small program that calls your code and checks the answer. Tests let you change code without fear. After every change you run them, and in seconds you know if something broke.

Our tests will:

- run **fast** (no real network, no real Postgres),
- be **isolated** (each test gets a fresh, empty database),
- call the API the way a client would.

## Idea: the test pyramid

@@ stack | Figure 15.1: more small tests, fewer big ones.
Few end-to-end tests|the real server, a real database, a browser|red
Some API tests|call routes in memory, test DB, fakes for outside services|yellow
Many unit tests|one function at a time: services, validators, helpers|green
@@ end

TaskFlow mostly uses **API tests**: they go through route, service, repository and a throw-away database in one go. That gives a lot of confidence for little code.

## Steps

::: {.step}
Step 1: install pytest
:::

```bash
uv add --dev pytest pytest-asyncio httpx
mkdir tests
touch tests/__init__.py
```

Our routes are `async`, so tests are `async` too. `pytest-asyncio` runs them. Tell it to do so automatically. In `pyproject.toml` add:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
```

With `asyncio_mode = "auto"` you just write `async def test_...` and no extra marker.

::: {.step}
Step 2: a first test
:::

`tests/test_health.py`:

```python
from httpx import ASGITransport, AsyncClient

from app.main import app


async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

```bash
uv run pytest
# -> 1 passed in 0.05s
```

`AsyncClient` with `ASGITransport` calls your app **in memory**. No server, no port. It is fast.

A test is a function whose name starts with `test_`. `assert` checks a claim. If it is false, pytest shows you both sides.

::: {.step}
Step 3: a fixture for a clean database
:::

A **fixture** is setup code that tests receive as an argument. We need one that gives every test a fresh in-memory database and swaps it in with `dependency_overrides` (chapter 7).

`tests/conftest.py` (pytest loads this file automatically):

```python
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_session
from app.main import app


@pytest.fixture
async def client():
    engine = create_async_engine(
        "sqlite+aiosqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_session():
        async with Session() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
    await engine.dispose()
```

How it works:

- `sqlite+aiosqlite://` with no file name means a database **in memory**.
- `StaticPool` makes all connections share that one in-memory database. Without it each connection would see an empty one.
- `Base.metadata.create_all` builds the tables. (In tests this is fine. Real environments use Alembic.)
- `app.dependency_overrides[get_session]` tells FastAPI: "when a route asks for a session, give it the test one".
- Code after `yield` is cleanup. It runs after each test.

This is why we used dependencies for the session: **testing is easy when the outside world is injected.**

Add a second helper and fixture to the same file, for logging in:

```python
async def register_and_login(client, email="a@x.com", password="secret123"):
    await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    r = await client.post("/api/v1/auth/login", data={"username": email, "password": password})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
async def auth(client):
    return await register_and_login(client)
```

::: {.step}
Step 4: test the real behaviour
:::

`tests/test_tasks.py`:

```python
from tests.conftest import register_and_login


async def test_create_and_get_task(client, auth):
    r = await client.post("/api/v1/tasks", json={"title": "Learn FastAPI"}, headers=auth)
    assert r.status_code == 201
    task = r.json()
    assert task["title"] == "Learn FastAPI" and task["done"] is False
    r = await client.get(f"/api/v1/tasks/{task['id']}", headers=auth)
    assert r.status_code == 200


async def test_validation_error(client, auth):
    r = await client.post("/api/v1/tasks", json={"title": ""}, headers=auth)
    assert r.status_code == 422


async def test_needs_login(client):
    assert (await client.get("/api/v1/tasks")).status_code == 401


async def test_cannot_read_other_users_task(client, auth):
    await client.post("/api/v1/tasks", json={"title": "secret"}, headers=auth)
    other = await register_and_login(client, email="b@x.com")
    r = await client.get("/api/v1/tasks/1", headers=other)
    assert r.status_code == 404
```

The last test protects the most important rule: users must not see each other's data. Write such a test for every rule you care about.

```bash
uv run pytest -q
# -> .....                                                [100%]
# -> 5 passed
```

## What to test: a checklist for every route

@@ grid 2 | Figure 15.2: five kinds of cases.
Happy path|a valid request gives 200, 201 or 204;the right body|green
Bad input|empty, too long, wrong type gives 422|yellow
Not found|a missing id gives 404|blue
Not allowed|no token gives 401, other user's data gives 404 or 403|red
@@ end

## Test a failing outside service with a fake

Never call a real LLM or payment API in a test. It is slow, costs money, and fails randomly. Our `stream_answer` takes the client as an **argument**, so a fake is easy:

```python
from app.services.llm_service import stream_answer


class FakeChunk:
    def __init__(self, text):
        self.choices = [type("C", (), {"delta": type("D", (), {"content": text})()})()]


class FakeStream:
    def __init__(self, parts):
        self.parts = parts

    def __aiter__(self):
        self._it = iter(self.parts)
        return self

    async def __anext__(self):
        try:
            return FakeChunk(next(self._it))
        except StopIteration:
            raise StopAsyncIteration


class FakeClient:
    def __init__(self, parts):
        self.chat = type("Chat", (), {"completions": self})()
        self.parts = parts

    async def create(self, **kwargs):
        return FakeStream(self.parts)


async def test_stream_answer():
    pieces = [p async for p in stream_answer(FakeClient(["Hel", "lo", "!"]), "model", "hi")]
    assert pieces == ["Hel", "lo", "!"]
```

For a route that uses `get_llm_client`, override that dependency the same way as the session.

## Unit tests for the service

Services have no HTTP in them, so they are easy to test alone. With a fake repository (just a class with the same methods), you test the **rules** without a database:

```python
import pytest
from app.core.exceptions import TaskNotFound
from app.services.task_service import TaskService


class FakeRepo:
    def __init__(self, task=None):
        self.task = task

    async def get(self, task_id):
        return self.task


async def test_get_task_not_found():
    service = TaskService(FakeRepo(task=None))
    with pytest.raises(TaskNotFound):
        await service.get_task(owner_id=1, task_id=99)
```

`pytest.raises` passes when the code raises that error.

## Useful pytest tools

| Tool | Use |
| --- | --- |
| `pytest -q` | quiet output |
| `pytest tests/test_tasks.py::test_delete` | run one test |
| `pytest -k "login"` | run tests with "login" in the name |
| `pytest -x` | stop at the first failure |
| `pytest --lf` | re-run only the last failures |
| `@pytest.mark.parametrize` | run one test with many inputs |

Parametrize example:

```python
import pytest

@pytest.mark.parametrize("title", ["", "x" * 101])
async def test_bad_titles(client, auth, title):
    r = await client.post("/api/v1/tasks", json={"title": title}, headers=auth)
    assert r.status_code == 422
```

This runs twice: once for an empty title, once for a title of 101 characters.

## Tests in CI

Run the same command on every push (chapter 16 shows GitHub Actions): `uv run pytest`. A red test blocks the merge.

::: {.box .checkpoint}
**Folder now**

```
tests/
├── __init__.py
├── conftest.py        # client + auth fixtures, a fresh DB per test
├── test_health.py
└── test_tasks.py
```

**Checkpoint:** `uv run pytest` is green. Break something on purpose (return `404` for a created task) and see the test fail, then fix it.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Tests that share data, so the order changes the result. Give each test a fresh database.
- Calling real external services (LLM, email, payments).
- Forgetting `app.dependency_overrides.clear()`, so overrides leak into other tests.
- Only testing the happy path.
- Testing the framework (does FastAPI return 422?) instead of **your** rules.
- Using a file-based database in tests and leaving files behind.
- Sleeping in tests (`time.sleep`). Use fakes or small timeouts.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: How do you test a FastAPI app?**
Use `httpx.AsyncClient` with `ASGITransport` (or `TestClient`) to call the app in memory, override dependencies (database, auth, outside clients) and assert on status and JSON.

**Q: What is a fixture?**
Reusable setup (and cleanup) that pytest passes into tests by argument name.

**Q: How do you avoid calling a real LLM in tests?**
Inject the client as a dependency or argument and replace it with a fake that returns fixed data.

**Q: Unit test vs integration test?**
A unit test checks one piece alone. An integration test checks several pieces working together, such as route + service + database.

**Q: What is `parametrize`?**
It runs one test function with many sets of inputs.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Write tests for `PATCH` (change `done`) and `DELETE` (then `GET` gives 404).
2. Write a test that registering the same email twice gives `409`.
3. Write a test that a wrong password gives `401`.
4. Use `parametrize` to test several bad registration bodies (short password, bad email).
5. Override `get_llm_client` with a fake and test `/chat/stream` returns the pieces.
6. **Think:** why do we use `StaticPool` for an in-memory SQLite test database?
:::
