# 16. Testing with pytest, and packaging with uv

How do you know your code works? You run it and look. That works once. After ten changes, you cannot re-check everything by hand. A **test** is a small program that checks your code and tells you if it broke. Tests let you change code without fear, which is why every serious project has them.

## What a test is

A test is a function that calls your code and uses `assert` to state what must be true. If the claim is false, the test **fails** and shows you both sides.

Suppose `calc.py` has:

```python
def divide(a, b):
    if b == 0:
        raise ValueError("b must not be zero")
    return a / b
```

A test file `test_calc.py`:

```python
import pytest
from calc import divide

def test_divide():
    assert divide(6, 3) == 2

def test_zero():
    with pytest.raises(ValueError, match="zero"):
        divide(1, 0)
```

Run it:

```bash
uv add --dev pytest
uv run pytest -q
# -> ..                                                  [100%]
# -> 2 passed
```

Rules `pytest` uses to find tests: files named `test_*.py`, functions named `test_*`. Nothing else to register. Each dot is one passing test.

- `assert divide(6, 3) == 2` states a fact. If it is false, pytest prints the real value.
- `pytest.raises(ValueError)` says "this code **must** raise that error". If it does not, the test fails. The `match` checks the message.

## What to test

For each function, think of four kinds of input:

@@ grid 2 | Figure 16.1: the four kinds of test case.
Normal|a typical valid input|green
Edge|empty, zero, one item, the biggest and smallest|yellow
Bad|wrong type or value; it should raise|red
Regression|the exact input of a bug you fixed;so it never returns|blue
@@ end

## Many cases, one test: `parametrize`

```python
@pytest.mark.parametrize("a, b, want", [(4, 2, 2), (9, 3, 3), (1, 4, 0.25)])
def test_many(a, b, want):
    assert divide(a, b) == want
```

pytest runs this function three times, once for each row, and reports each separately. Good for many similar cases.

## Fixtures: reusable setup

A **fixture** is a function that prepares something for tests. A test uses it just by naming it as a parameter.

```python
@pytest.fixture
def numbers():
    return [1, 2, 3]

def test_sum(numbers):
    assert sum(numbers) == 6
```

pytest sees the parameter `numbers`, finds the fixture with that name, runs it and passes the result in. Each test gets a **fresh** value, so tests cannot affect each other. Fixtures can also clean up: write `yield value`, and the code after `yield` runs when the test ends. Fixtures shared by many files go into a file named `conftest.py`.

Built-in fixtures you will use: `tmp_path` (a temporary folder, deleted later) and `monkeypatch`.

```python
def test_tmp(tmp_path):
    file = tmp_path / "a.txt"
    file.write_text("x")
    assert file.read_text() == "x"
```

## Replacing the outside world: mocking

A test must be **fast** and **repeatable**. It must not call a real website, send a real email or call a paid AI model. So you swap the real thing for a fake one.

```python
from unittest.mock import Mock

def test_mock():
    fake = Mock(return_value=5)
    assert fake(1) == 5
    fake.assert_called_once_with(1)
```

A `Mock` accepts any call, returns what you set, and remembers how it was called. `monkeypatch.setattr(module, "name", replacement)` swaps a real thing for a fake during one test, then puts it back.

Even better than mocking is **designing for tests**: pass the dependency in as an argument (the LLM client, the database). In the test you hand in a tiny fake class. This is what FastAPI's `Depends` and `dependency_overrides` are for.

## Testing async code

Install `pytest-asyncio`, then mark async tests:

```python
@pytest.mark.asyncio
async def test_async():
    assert await fetch(2) == 4
```

Or set `asyncio_mode = "auto"` in `pyproject.toml` and write `async def test_...` with no marker (that is what the FastAPI booklet does).

## Habits of good tests

- One idea per test, with a name that says it: `test_divide_by_zero_raises`.
- Tests do not depend on each other or on the order.
- No real network, no real sleeping.
- Run them often, and in CI on every push.
- A failing test first, then the fix (and the test stays as a guard).

## Packaging with uv

A **package manager** installs libraries. `uv` is the fast, modern one used in all these booklets.

| Task | Command |
| --- | --- |
| create a project | `uv init myapp` |
| add a library | `uv add httpx` |
| add a dev-only library | `uv add --dev pytest` |
| remove a library | `uv remove httpx` |
| run a script in the project | `uv run main.py` |
| install everything listed | `uv sync` |

Two files matter:

- **`pyproject.toml`** lists what the project **wants**: its name, Python version and libraries.
- **`uv.lock`** records the **exact versions** that were installed, so another computer gets the identical setup. Commit both to git.

A **virtual environment** (the `.venv` folder) holds the installed libraries for this project only, so projects never fight over versions. `uv run` uses it automatically. Never commit `.venv`.

## Project layout

```
myapp/
├── pyproject.toml
├── uv.lock
├── src_or_app/
│   ├── __init__.py
│   └── main.py
└── tests/
    └── test_main.py
```

Keep tests in a separate `tests/` folder, next to your code, not inside it.

::: {.box .checkpoint}
**Checkpoint:** `uv run pytest` is green for a function you wrote. You made it fail on purpose, read the message, and fixed it.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Only testing the happy path.
- Tests that depend on each other's order.
- Calling real services in tests.
- A test with no `assert`, which always passes and proves nothing.
- Committing `.venv`, or not committing `uv.lock`.
- Installing libraries globally with `pip` instead of into the project.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: What is a fixture?** Reusable setup (and cleanup) injected into tests by parameter name.

**Q: What is mocking?** Replacing a real dependency with a fake one so the test is fast and isolated.

**Q: Unit test vs integration test?** A unit test checks one piece alone. An integration test checks several pieces working together.

**Q: What does `parametrize` do?** Runs one test function over several sets of inputs.

**Q: `pyproject.toml` vs `uv.lock`?** The first states what you want, the second pins the exact versions installed.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Write three tests for `is_even(n)`: normal, edge (0) and negative.
2. Use `parametrize` to test a `slugify(text)` function with five inputs.
3. Test that `safe_int("abc")` returns `None`, using `pytest.raises` for the unsafe version.
4. Use `tmp_path` to test a function that writes a file.
5. Write a function that takes a `client` argument and test it with a fake class.
6. **Think:** why is a test that calls a real paid API a bad test?
:::
