# A dataclass with validation

Write a dataclass `Task` with fields:

| field | type | default |
|---|---|---|
| `title` | str | (required) |
| `priority` | int | `2` (1 = high, 3 = low) |
| `tags` | list[str] | empty list (**not shared** between instances) |
| `done` | bool | `False` |

- In `__post_init__`: strip the title, raise `ValueError` if it's empty or if `priority` is not 1, 2 or 3.
- Make instances **sortable**: by `priority` first, then `title`. Careful: `order=True` compares fields **in definition order**, and `title` comes first. The standard trick: add a first field `sort_index: tuple = field(init=False, repr=False)`, set it in `__post_init__` to `(self.priority, self.title)`, and keep `order=True`.
- Also write a frozen dataclass `TaskId(value: int)` that is hashable and immutable.

```python
Task("  Write tests ").title                 # -> "Write tests"
sorted([Task("b", 2), Task("a", 2), Task("z", 1)])  # -> z, a, b
Task("x").tags.append("y"); Task("x").tags  # -> []
```
