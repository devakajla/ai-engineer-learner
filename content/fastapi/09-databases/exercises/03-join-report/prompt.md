# JOIN + GROUP BY report

`setup(conn)` (given) creates `users(id, email)` and `tasks(id, title, done, owner_id)` with sample data.

Write **one SQL query each** (no Python loops over rows to aggregate):

- `open_tasks_per_user(conn)` → list of `(email, open_count)` for **every** user (including users with 0 open tasks), ordered by `open_count` desc, then email asc. Open = `done = 0`.
- `busiest_users(conn, min_open)` → emails of users with **at least** `min_open` open tasks, ordered by email (use `HAVING`).
- `add_index(conn)` → create an index named `ix_tasks_owner_done` on `tasks(owner_id, done)`.

```python
open_tasks_per_user(conn)   # -> [("ana@x.io", 2), ("dev@x.io", 1), ("zed@x.io", 0)]
```
