# A tiny repository with sqlite3

Using an **in-memory** database passed in as `conn` (`sqlite3.connect(":memory:")`), write:

- `create_schema(conn)` — creates table `notes(id INTEGER PRIMARY KEY, title TEXT NOT NULL, body TEXT NOT NULL DEFAULT '')`
- `add_note(conn, title, body="") -> int` — inserts, **commits**, returns the new id
- `get_note(conn, note_id) -> dict | None` — returns `{"id", "title", "body"}` or `None`
- `search(conn, text) -> list[dict]` — notes whose title contains `text` (case-insensitive, use `LIKE`), ordered by id

All queries **must be parameterized** (`?`), including the `LIKE` pattern (build `%text%` in Python and pass it as a parameter).

```python
conn = sqlite3.connect(":memory:")
create_schema(conn)
nid = add_note(conn, "Learn SQL")
get_note(conn, nid)       # -> {"id": 1, "title": "Learn SQL", "body": ""}
search(conn, "sql")       # -> [{"id": 1, "title": "Learn SQL", "body": ""}]
```
