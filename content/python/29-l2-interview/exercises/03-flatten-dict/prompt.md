# Flatten nested config

Config often arrives nested; env vars and logs want it flat. Write:

- `flatten(d, sep=".")` → a new dict with dotted keys. Nested dicts are flattened recursively; **lists and other values are kept as values**; empty nested dicts disappear.
- `unflatten(flat, sep=".")` → the inverse. Raise `ValueError` on conflicts like `{"a": 1, "a.b": 2}`.

Use a **generator** helper (`yield` pairs) for `flatten`.

```python
flatten({"db": {"host": "x", "port": 5432}, "debug": True, "tags": ["a"]})
# -> {"db.host": "x", "db.port": 5432, "debug": True, "tags": ["a"]}
unflatten({"db.host": "x", "db.port": 5432})
# -> {"db": {"host": "x", "port": 5432}}
```
