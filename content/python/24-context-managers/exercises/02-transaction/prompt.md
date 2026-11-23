# A transaction context manager

`FakeConnection` (in the starter) records calls. Write `transaction(conn)` with `@contextmanager`:

- calls `conn.begin()` on enter and yields `conn`
- on success: `conn.commit()`
- on exception: `conn.rollback()` and **re-raise**
- never both commit and rollback

```python
conn = FakeConnection()
with transaction(conn) as c:
    c.execute("INSERT ...")
conn.log   # -> ["begin", "execute INSERT ...", "commit"]
```
