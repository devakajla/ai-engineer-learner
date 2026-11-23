# Independent config copies

You keep a base config and create per-environment versions:

```python
BASE = {"db": {"host": "localhost", "port": 5432}, "features": ["auth"]}
```

Write `make_env_config(base, env)` that returns a **new** config where:

- `"env"` is set to `env`
- for `env == "prod"`: `db.host` becomes `"db.internal"` and `"metrics"` is appended to `features`

The `base` dict (including nested dicts/lists) must **never** be modified, and two returned configs must not share nested objects.

```python
prod = make_env_config(BASE, "prod")
prod["db"]["host"]          # -> "db.internal"
BASE["db"]["host"]          # -> "localhost"   (unchanged)
BASE["features"]            # -> ["auth"]      (unchanged)
```
