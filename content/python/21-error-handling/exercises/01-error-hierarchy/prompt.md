# An app error hierarchy

Create:

- `AppError(Exception)` with a class attribute `status_code = 500` and a method `to_dict()` returning `{"error": <class name>, "message": str(self)}`
- `NotFoundError(AppError)`: `status_code = 404`, constructor `NotFoundError(resource, resource_id)`, message `"<resource> <resource_id> not found"`, and it stores both as attributes
- `ConflictError(AppError)`: `status_code = 409`
- `ValidationError(AppError)`: `status_code = 422`, constructor `ValidationError(field, message)`, `str()` is `"<field>: <message>"`, and `to_dict()` also includes `"field": <field>`

```python
e = NotFoundError("Task", 7)
str(e)          # -> "Task 7 not found"
e.status_code   # -> 404
e.to_dict()     # -> {"error": "NotFoundError", "message": "Task 7 not found"}
isinstance(e, AppError)   # -> True
```
