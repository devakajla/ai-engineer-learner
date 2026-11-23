# Settings from the environment

Using `pydantic-settings`, create:

```python
class Settings(BaseSettings):
    app_name: str = "Notes"
    debug: bool = False
    max_page_size: int = 50
```

- `get_settings()` returns a **new** `Settings()` each call (so tests can change env vars).
- `GET /config` returns the three values from `get_settings()`:

```text
(no env vars)                         -> {"app_name": "Notes", "debug": false, "max_page_size": 50}
APP_NAME=TaskFlow DEBUG=true MAX_PAGE_SIZE=10
                                      -> {"app_name": "TaskFlow", "debug": true, "max_page_size": 10}
```

If `MAX_PAGE_SIZE=abc`, `get_settings()` must raise a validation error (pydantic-settings does this for you — don't catch it).

> In real apps you'd cache settings with `@lru_cache` (lesson 8). Here we keep it uncached so the tests can change env vars.
