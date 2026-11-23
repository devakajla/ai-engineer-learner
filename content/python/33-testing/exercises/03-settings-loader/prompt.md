# Load settings from a file and the environment

Write `load_settings(path)`:

- Start from the defaults `{"debug": False, "port": 8000, "name": "app"}`.
- `path` is a `pathlib.Path` to a JSON file. If the file does **not exist**, use only the defaults. If it exists, its keys replace the defaults. If the JSON is broken, or the top level is not an object (dict), raise `ValueError`.
- Then the environment variable `APP_PORT`, if set, replaces `port`. It must be converted to `int`. If it is not a whole number, raise `ValueError`.
- Return a **new** dict. Never change a shared defaults dict between calls.

```python
load_settings(Path("missing.json"))          # -> {"debug": False, "port": 8000, "name": "app"}
# file {"port": 9000, "debug": true}, APP_PORT=7000
# -> {"debug": True, "port": 7000, "name": "app"}
```

**Think first:** Which should win, the file or the environment? What if two calls both change the defaults?

**Hint:** `path.exists()`, `json.loads(path.read_text())`, `os.environ.get("APP_PORT")`, and start from `dict(DEFAULTS)` (a copy) each time.
