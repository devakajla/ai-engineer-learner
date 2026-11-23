---
title: Testing FastAPI apps
summary: Write a real test suite with pytest, fixtures, separate test databases, dependency overrides and fakes. Learn what to test so your tests catch bugs.
plan_ids: [PY-11, FA-02]
---

Until now, this app checked your code with its own tests. A real backend has **its own test suite** that runs on every change. Then you can refactor with confidence (like the async rewrite in step 12) and know quickly if something broke.

This lesson teaches you to write that suite. The goal is tests that **catch bugs**, not tests that only pass.

## The testing pyramid

| Level | What it checks | Speed | How many |
|---|---|---|---|
| **Unit** | one function or class alone (a service with a fake repository) | very fast | many |
| **Integration** | the API with a real database, using `TestClient` | fast | a good number |
| **End-to-end** | the full deployed system with real HTTP | slow | few |

For APIs, **integration tests through HTTP** give the most trust for each test. One request checks routing, validation, dependencies, the service, the repository and SQL, all together.

## pytest basics

**pytest** is the standard Python test tool. A test is a function whose name starts with `test_`. You check things with a plain `assert`.

```python
import pytest

def test_create_task(client):                # "client" is a fixture, given by name
    r = client.post("/api/v1/tasks", json={"title": "x"})
    assert r.status_code == 201

@pytest.mark.parametrize("payload", [{}, {"title": ""}, {"title": "x", "priority": "urgent"}])
def test_create_validation(client, payload):  # one test, run once for each payload
    assert client.post("/api/v1/tasks", json=payload).status_code == 422
```

- When an `assert` fails, pytest shows both sides clearly.
- `@pytest.mark.parametrize("name", [values])` runs the same test with many inputs. Each one is reported separately.
- Handy options: `pytest -x` (stop at the first failure), `-k word` (run only tests whose name has `word`), `-q` (quiet), `--lf` (re-run the last failures).

## Fixtures

A **fixture** prepares something a test needs (and cleans up after). A test asks for it by writing its **name as a parameter**.

```python
@pytest.fixture
def repo():
    return InMemoryTaskRepository()          # a fresh one for every test

@pytest.fixture
def client(repo):                            # a fixture can use another fixture
    app.dependency_overrides[get_task_repository] = lambda: repo
    yield TestClient(app)                    # the test runs here
    app.dependency_overrides.clear()         # clean-up, after the test
```

- Code before `yield` is set-up. Code after `yield` is clean-up. (The same idea as `yield` dependencies in lesson 8.)
- By default, a fixture runs again for **each test** (`function` scope), so tests do not affect each other. Other scopes (`module`, `session`) share one for many tests, for example an expensive database engine.
- Put fixtures that many files use in **`tests/conftest.py`**. pytest finds it by itself. You do not import anything.

## Worked example: write tests that catch bugs

Exercise 1 gives you an app and asks **you** to write the tests. Your tests are then run against the correct app (they must pass) and against broken copies of it (they must **fail**). Here is the same pattern for a different problem: a **delivery fee** endpoint.

The app:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

class FeeIn(BaseModel):
    km: float = Field(gt=0)
    express: bool = False

@app.post("/fee")
def fee(body: FeeIn):
    if body.km > 50:
        raise HTTPException(400, "Too far")
    amount = 20 + 5 * body.km          # base 20, then 5 per km
    if body.express:
        amount *= 2                    # express costs double
    return {"fee": round(amount, 2)}
```

The rules in words: the fee is 20 plus 5 per km. Express doubles it. More than 50 km gives `400`. `km` must be above 0.

**Step 1.** Test the normal case, and check the **body**, not only the status code.

```python
from fastapi.testclient import TestClient
client = TestClient(app)

def test_basic_fee():
    r = client.post("/fee", json={"km": 2})
    assert r.status_code == 200
    assert r.json() == {"fee": 30.0}
```

If a bug changed the formula, only the body check would catch it.

**Step 2.** Test every rule on its own.

```python
def test_express_doubles():
    assert client.post("/fee", json={"km": 2, "express": True}).json() == {"fee": 60.0}
```

**Step 3.** Test the **edges**. Bugs hide at boundaries, so test exactly on and just past the limit. Use `parametrize`.

```python
import pytest

@pytest.mark.parametrize("km, status", [(50, 200), (50.1, 400), (0.1, 200)])
def test_distance_limit(km, status):
    assert client.post("/fee", json={"km": km}).status_code == status
```

A bug that changed `> 50` to `>= 50` fails the `(50, 200)` case. A bug that changed it to `> 51` fails `(50.1, 400)`.

**Step 4.** Test invalid input, and the rounding.

```python
@pytest.mark.parametrize("body", [{}, {"km": 0}, {"km": -3}, {"km": "far"}])
def test_invalid_body(body):
    assert client.post("/fee", json=body).status_code == 422

def test_rounding():
    assert client.post("/fee", json={"km": 0.3333}).json() == {"fee": 21.67}
```

**Step 5.** Ask the key question: **"If someone broke this rule, would a test fail?"** Try it yourself: change `5 * body.km` to `4 * body.km` and run the tests. A good suite turns red.

## Test databases that are separate and clean

Tests must **never** touch your real database, and each test should begin from a known, empty state. Common ways:

- **A temporary SQLite file for each test.** Simple, and what we use in the project. Create the schema, yield a session, delete the file.
- **One transaction per test, rolled back at the end.** Fast with Postgres.
- **testcontainers.** Starts a real Postgres in Docker for the test run. The closest to production.

You connect it with a dependency override, as in lesson 8:

```python
app.dependency_overrides[get_db] = override_get_db
```

Because routes receive the session through dependency injection, nothing else changes.

pytest gives you a built-in fixture called `tmp_path`: a fresh temporary folder for each test. Use it for the temporary database file.

## Fake the outside world

Your tests must **not** call real AI model APIs, payment services or email servers. They are slow, they fail at random, and they cost money.

Since outside clients arrive through dependencies, **override them with a fake**: a simple class you control.

```python
class FakeWeather:
    def __init__(self, temp=20.0, error=None):
        self.temp = temp
        self.error = error
        self.cities = []                      # remember what we were asked

    async def current_temp(self, city):
        self.cities.append(city)
        if self.error:
            raise self.error
        return self.temp
```

```python
fake = FakeWeather(temp=12.34)
app.dependency_overrides[get_weather_client] = lambda: fake

r = client.get("/weather/Pune")
assert r.json()["temp_c"] == 12.3
assert fake.cities == ["Pune"]                # the right city was passed on
```

Also test the **sad paths**: a timeout, a server error from the provider, an unknown city. That is where real production bugs live.

```python
app.dependency_overrides[get_weather_client] = lambda: FakeWeather(error=TimeoutError())
client = TestClient(app, raise_server_exceptions=False)
assert client.get("/weather/Pune").status_code == 503
```

`raise_server_exceptions=False` makes `TestClient` return an unexpected error as a `500` response, instead of raising it inside your test.

## Async apps

`TestClient` also works for async apps. It starts the event loop for you. You only need special tools (`httpx.AsyncClient` with `pytest-asyncio`) when you want to call `await` code directly in a test.

## What to test: a checklist for each endpoint

- The happy path: the status code **and** the body (fields, values and types).
- Validation: a missing or invalid field gives `422`.
- Not found: `404` with the correct body.
- Side effects: after `DELETE`, a `GET` gives `404`. After `PATCH`, the fields you did not send stay the same.
- Rules and edges: empty lists, limits, filters, sorting, permissions (later: other users' tasks).

## Good tests catch bugs

A test that passes even when the code is broken is worse than no test. It gives false confidence. So ask: **"If someone broke this behaviour, would a test fail?"**

This idea is behind **mutation testing**: you deliberately put small bugs ("mutants") into the code and check that your tests fail ("kill" them). The exercises and the project checkpoint do this to **your** tests.

Also: **test behaviour, not inner details.** Check HTTP responses and visible state, not private methods. Then you can refactor without breaking the tests.

## A little deeper (optional)

- **Coverage** shows which lines your tests ran: `uv run pytest --cov=app --cov-report=term-missing` (needs `pytest-cov`). It is a useful guide but a bad goal. 100% coverage with weak asserts still catches nothing.
- **CI** (Continuous Integration) runs your tests automatically on every push. A failing build blocks the merge. You will set this up in Level 3.
- An **`httpx` mock library** such as `respx` can fake web calls at the HTTP level.
- A **factory fixture** is a fixture that returns a helper function, such as `make_task(title="x")`, that creates data through the API. It keeps tests short.

## Common mistakes

- Tests that share state, so one test's data breaks another. Use fresh, per-test fixtures.
- Using the real database or real outside APIs.
- Only testing the happy path.
- Checking only `status_code == 200` and not the body.
- Forgetting `app.dependency_overrides.clear()`.

## Interview corner

- **Q: How do you test a FastAPI endpoint that uses a database?** Override `get_db` with a session to an isolated test database (a temp SQLite file, a rolled-back transaction, or testcontainers), and call the endpoint with `TestClient`.
- **Q: How do you test code that calls an outside API?** Inject the client as a dependency and override it with a fake (or mock the HTTP calls). Test the failure cases too.
- **Q: Unit vs integration tests?** A unit test checks one part with fakes and is very fast. An integration test checks several real parts together, such as the API and the database.
- **Q: Is 100% coverage enough?** No. Coverage shows which lines ran, not whether the behaviour was checked. Weak asserts give high coverage and no safety.

## Summary

- Pyramid: many unit tests, a solid set of integration tests (API plus database), few end-to-end tests.
- Fixtures (with `yield` for clean-up), `conftest.py`, and `parametrize`.
- A separate, fresh test database for each test, connected with `dependency_overrides`.
- Fakes for outside services. Test the sad paths.
- A good test fails when the behaviour breaks. Think about "mutants" and test the edges.
