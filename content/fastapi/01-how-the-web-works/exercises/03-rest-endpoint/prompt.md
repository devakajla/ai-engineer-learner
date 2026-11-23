# Design the REST endpoint

Write `rest_endpoint(action, resource, item_id=None)` that returns the `(method, path)` a REST API should use.

| action | method | path |
|---|---|---|
| `"list"` | `GET` | `/<resource>` |
| `"create"` | `POST` | `/<resource>` |
| `"read"` | `GET` | `/<resource>/<id>` |
| `"replace"` | `PUT` | `/<resource>/<id>` |
| `"update"` | `PATCH` | `/<resource>/<id>` |
| `"delete"` | `DELETE` | `/<resource>/<id>` |

```python
rest_endpoint("list", "tasks")        # -> ("GET", "/tasks")
rest_endpoint("update", "tasks", 42)  # -> ("PATCH", "/tasks/42")
```

Raise `ValueError` for an unknown action, or when an action that needs an id gets `item_id=None`.
