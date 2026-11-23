# Signup form validation

Write a Pydantic model `SignupForm`:

| field | rules |
|---|---|
| `username` | 3–20 chars; only letters, digits and `_`; **lowercased** in the result |
| `email` | must contain exactly one `@` and a `.` after it; **stripped + lowercased** |
| `password` | at least 8 chars, at least one digit and one uppercase letter |
| `password_confirm` | must equal `password` (model validator) |
| `age` | int, optional (`None` allowed); if given, ≥ 13 |

Use `Field` for simple constraints, `@field_validator` for per-field rules and `@model_validator(mode="after")` for the match.

```python
SignupForm(username="Dev_22", email=" Dev@X.io ", password="Secret123", password_confirm="Secret123")
# -> username="dev_22", email="dev@x.io"
```
