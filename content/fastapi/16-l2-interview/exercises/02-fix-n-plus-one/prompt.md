# Interview task: fix the slow endpoint (20 min)

`GET /users` returns every user with their number of **open** tasks and the title of their most recent task. It's correct but slow: it runs **1 + 2N** queries. The interviewer asks you to make it run in **at most 2 queries** without changing the response.

```json
[{"id": 1, "email": "a@x.io", "open_tasks": 2, "latest_task": "Ship v2"}, ...]
```

- ordered by user id
- `latest_task` = title of the task with the highest id, or `null` if the user has no tasks
- `open_tasks` counts tasks with `done = False`

Use `selectinload` (and compute in Python) **or** aggregate queries. The tests count SQL statements. Models, data and the slow version are in the starter — keep the models and `seed()` unchanged.
