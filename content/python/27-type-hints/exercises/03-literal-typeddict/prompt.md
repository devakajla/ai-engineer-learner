# Literal and TypedDict

Define:

```python
Status = Literal["todo", "doing", "done"]

class TaskDict(TypedDict):
    id: int
    title: str
    status: Status
```

Then write:

- `next_status(status: Status) -> Status` — todo → doing → done → done
- `parse_task(data: dict[str, object]) -> TaskDict` — validates at runtime: `id` is an int, `title` a non-empty str, and `status` one of the Literal's values (read them with `typing.get_args(Status)` — don't repeat the strings). Raise `ValueError` on any problem.

```python
next_status("todo")                                   # -> "doing"
parse_task({"id": 1, "title": "x", "status": "done"}) # -> {"id": 1, "title": "x", "status": "done"}
parse_task({"id": 1, "title": "x", "status": "blocked"})   # ValueError
```
