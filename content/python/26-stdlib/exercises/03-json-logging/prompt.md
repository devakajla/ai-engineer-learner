# JSON encoding and logging

1. `to_json(obj)` → `json.dumps` with `sort_keys=True` and a `default=` function that encodes:
   - `datetime` → ISO string
   - `Decimal` → string
   - `set` → **sorted** list
   - anything else → `TypeError`

2. `import_rows(rows)` → each row is a dict that should have an int `"id"`. Return the list of valid ids. Use a module-level `logger = logging.getLogger(__name__)`:
   - log `WARNING` `"skipping row %s: missing id"` (with the row index) for rows without `"id"`
   - log `INFO` `"imported %d rows"` at the end
   - **no `print`**

```python
to_json({"at": datetime(2026, 1, 1, tzinfo=UTC), "price": Decimal("9.99"), "tags": {"b", "a"}})
# -> '{"at": "2026-01-01T00:00:00+00:00", "price": "9.99", "tags": ["a", "b"]}'
```
