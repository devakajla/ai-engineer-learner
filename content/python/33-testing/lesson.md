---
title: Testing with pytest
summary: Write small automatic checks with pytest - asserts, errors, parametrize, fixtures, temporary files, monkeypatch and fakes - and design code that is easy to test.
plan_ids: [PY-10]
---

A **test** is a small piece of code that runs your code and checks the result. You run all your tests with one command. If you change something and break an old feature, a test fails and tells you **right away**, before a user finds the bug.

You have been using tests all through this course: every exercise has a `test_solution.py`. Now you learn to write them yourself.

## Your first test

pytest finds files named `test_*.py` and, inside them, functions named `test_*`. A test is a plain function with a plain `assert`.

```python
# file: test_math.py
def add(a, b):
    return a + b

def test_add():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, 1) == 0
```

Run it:

```bash
uv run pytest
```

pytest prints a dot for each pass and an `F` for each failure, with a clear message showing both values.

If an `assert` is false, the test **fails**. If the test function finishes with no error, it **passes**.

## Arrange, act, assert

Good tests have three parts. Keep them in this order:

1. **Arrange**: set up the data.
2. **Act**: call the code you test (once).
3. **Assert**: check the result.

```python
def total_price(prices, tax):
    return round(sum(prices) * (1 + tax), 2)

def test_total_price_with_tax():
    prices = [10, 20]                     # arrange
    result = total_price(prices, 0.1)     # act
    assert result == 33.0                 # assert
```

Name a test by **what it checks**: `test_total_price_with_tax`, not `test1`. When it fails, the name tells you what broke.

Test the normal case and the **edges**: empty input, zero, one item, a very big value, bad input.

## Testing that an error is raised

Use `pytest.raises` as a context manager (lesson 24). The test passes only if the error happens:

```python
import pytest

def divide(a, b):
    if b == 0:
        raise ValueError("b must not be zero")
    return a / b

def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(1, 0)

def test_divide_by_zero_message():
    with pytest.raises(ValueError, match="must not be zero"):
        divide(1, 0)
```

`match=` checks the error message with a pattern.

## Same test, many inputs: `parametrize`

Do not copy a test ten times. List the inputs once:

```python
import pytest

@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
])
def test_add_many(a, b, expected):
    assert add(a, b) == expected
```

pytest runs the test three times, and reports each one separately.

## Fixtures: shared setup

A **fixture** is a function that prepares something for tests. A test asks for it by writing its name as a parameter. Mark it with `@pytest.fixture`.

```python
import pytest

@pytest.fixture
def basket():
    return ["apple", "pear"]           # a fresh list for each test

def test_basket_size(basket):
    assert len(basket) == 2

def test_basket_change(basket):
    basket.append("fig")
    assert len(basket) == 3            # other tests are not affected
```

Each test gets a **new** result of the fixture, so tests cannot affect each other. Tests must not depend on the order they run in.

A fixture can also clean up. Use `yield`: the code before it is the setup, and the code after it is the cleanup (like `@contextmanager`, lesson 24):

```python
@pytest.fixture
def connection():
    conn = open_connection()
    yield conn                          # the test runs here
    conn.close()                        # cleanup runs even if the test fails
```

Fixtures used by many files go in a file called **`conftest.py`**. pytest finds it by itself, and you do not import anything.

## Built-in fixtures you will use a lot

### `tmp_path`: a private temporary folder

```python
import json

def save_json(path, data):
    path.write_text(json.dumps(data))

def test_save_json(tmp_path):                 # a new empty folder for this test
    file = tmp_path / "data.json"
    save_json(file, {"a": 1})
    assert json.loads(file.read_text()) == {"a": 1}
```

`tmp_path` is a `pathlib.Path` (lesson 15). Never write test files into your real folders.

### `monkeypatch`: change things for one test

`monkeypatch` changes an environment variable, an attribute or a dict **only during one test**, and puts everything back after it.

```python
import os

def get_mode():
    return os.environ.get("APP_MODE", "dev")

def test_get_mode_default(monkeypatch):
    monkeypatch.delenv("APP_MODE", raising=False)    # make sure it is not set
    assert get_mode() == "dev"

def test_get_mode_from_env(monkeypatch):
    monkeypatch.setenv("APP_MODE", "prod")
    assert get_mode() == "prod"
```

## Make your code easy to test: pass things in

Code that **creates its own helpers inside** is hard to test. Look at this:

```python
import time

def is_expired(created_at):
    return time.time() - created_at > 60       # uses the real clock!
```

To test it, you would have to wait 60 real seconds. A better way: **pass the thing in** as a parameter. This is called **dependency injection**.

```python
def is_expired(created_at, now):
    return now - created_at > 60

def test_is_expired():
    assert is_expired(created_at=0, now=61) is True
    assert is_expired(created_at=0, now=60) is False
```

No waiting, no luck needed. The same idea works for the clock, the network, the database and the email sender: take them as parameters (or in `__init__`), and use a **fake** in tests.

## Fakes: a pretend helper

A **fake** is a simple stand-in object that records what happened. A step-by-step example. We write a service that welcomes a new user by email. We do not want to send real emails in a test.

1. The service takes a `mailer` in `__init__`, and calls `mailer.send(to, text)`.
2. In the test, we write a `FakeMailer` that only stores the calls in a list.
3. We call the service, then look at the list.

```python
class WelcomeService:
    def __init__(self, mailer):
        self.mailer = mailer

    def welcome(self, name, email):
        if not email:
            raise ValueError("email is required")
        self.mailer.send(email, f"Welcome, {name}!")

class FakeMailer:
    def __init__(self):
        self.sent = []                       # a record of the calls

    def send(self, to, text):
        self.sent.append((to, text))

def test_welcome_sends_one_email():
    mailer = FakeMailer()
    service = WelcomeService(mailer)

    service.welcome("Ana", "ana@x.io")

    assert mailer.sent == [("ana@x.io", "Welcome, Ana!")]

def test_welcome_without_email_sends_nothing():
    mailer = FakeMailer()
    service = WelcomeService(mailer)

    with pytest.raises(ValueError):
        service.welcome("Ana", "")

    assert mailer.sent == []                 # nothing was sent
```

The second test is important: it checks that a failed action has **no side effects**.

### `unittest.mock`: ready-made fakes

Python has `unittest.mock.Mock`. It accepts any call and remembers it:

```python
from unittest.mock import Mock

mailer = Mock()
WelcomeService(mailer).welcome("Ana", "ana@x.io")
mailer.send.assert_called_once_with("ana@x.io", "Welcome, Ana!")
```

A hand-written fake is often clearer. Use a `Mock` when you only need to check that a call happened.

## What makes a good test

- **Fast**: no real network, no sleeping, no big files.
- **Independent**: it does not need another test to run first.
- **Clear**: when it fails, you know what broke.
- **One idea per test**: one reason to fail.
- It tests **behaviour** (what the code does), not tiny inner details that may change.

## Running tests

```bash
uv run pytest                       # everything
uv run pytest test_math.py          # one file
uv run pytest -k "divide"           # only tests with "divide" in the name
uv run pytest -x                    # stop at the first failure
uv run pytest -v                    # show each test name
```

## A little deeper (optional)

- **Test types.** *Unit tests* check one small piece. *Integration tests* check pieces working together (for example with a real test database). *End-to-end tests* check the whole app.
- **Coverage.** `pytest --cov` (with the `pytest-cov` library) shows which lines your tests ran. High coverage does not prove the tests are good, but low coverage shows what is untested.
- **Async tests.** With the `pytest-asyncio` plugin, you can write `async def test_...`.
- **FastAPI.** `fastapi.testclient.TestClient(app)` lets you call your API in a test, without starting a server. The FastAPI track uses it.
- **Test-driven development (TDD).** Write a failing test first, then the code that makes it pass.

## Common mistakes

- Tests that depend on each other or on the order.
- Tests that use the real clock, the real network or real files.
- A test with no `assert`. It always passes and proves nothing.
- Many `assert`s about many ideas in one test.
- Writing to real folders instead of `tmp_path`.
- Using a mutable default, or shared data, in fixtures so tests leak into each other.

## Interview corner

- **Q: What is a fixture?** A function that prepares data or resources for tests, which a test asks for by name. It can clean up after the test with `yield`.
- **Q: How do you test that code raises an error?** `with pytest.raises(SomeError):`.
- **Q: What is dependency injection, and why does it help with testing?** Passing helpers (clock, database, mailer) into the code instead of creating them inside. In tests you pass a fake.
- **Q: Fake or mock?** A fake is a simple working stand-in. A mock records calls and lets you check them. Both replace real dependencies in tests.
- **Q: How do you test code that reads an environment variable?** `monkeypatch.setenv` and `monkeypatch.delenv`.

## Summary

- A test is a function `test_...` with `assert`. Run with `uv run pytest`.
- Arrange, act, assert. Test normal cases and edges.
- `pytest.raises` for errors, `parametrize` for many inputs, fixtures (with `yield`) for setup.
- `tmp_path` gives a safe folder. `monkeypatch` changes env variables or attributes for one test.
- Pass dependencies in (clock, mailer, store) and use fakes. Good tests are fast, independent and clear.
