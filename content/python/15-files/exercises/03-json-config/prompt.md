# JSON config

Write `load_config(path, defaults)` that reads a JSON file (an object) and returns a dict with the file's values **on top of** `defaults`. If the file does not exist, return a copy of `defaults`. Do not change `defaults`.

```python
# file has {"port": 9000}
load_config(path, {"port": 8000, "debug": False})   # -> {"port": 9000, "debug": False}
# file missing
load_config(missing, {"port": 8000})                # -> {"port": 8000}
```

Hint: `Path(path).exists()` instead of error handling, and the `|` operator or `update` to merge.
