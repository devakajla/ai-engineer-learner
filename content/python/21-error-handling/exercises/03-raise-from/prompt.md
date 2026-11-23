# Wrap low-level errors, keep the cause

Write `ConfigError(Exception)` and `load_port(text)`:

- `text` is JSON like `'{"port": 8000}'`
- return the port as an int
- invalid JSON → raise `ConfigError("invalid JSON")` **chained** from the `json.JSONDecodeError`
- missing `"port"` key → raise `ConfigError("missing port")` chained from the `KeyError`
- port not an int between 1 and 65535 → `ConfigError("invalid port")` (no cause needed)

```python
load_port('{"port": 8000}')   # -> 8000
load_port('{oops')            # ConfigError("invalid JSON"), err.__cause__ is a JSONDecodeError
```

Keep each `try` block as small as possible.
