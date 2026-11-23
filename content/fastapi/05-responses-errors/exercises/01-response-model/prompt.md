# Hide the secrets

The in-memory `USERS` dict below stores password hashes. Create:

- a `UserOut` model with only `id`, `email`, `name`
- `GET /users/{user_id}` with `response_model=UserOut` that returns the stored user dict (the hash must be filtered out by the model)
- if the user doesn't exist → **404** with detail `"User not found"`

```text
GET /users/1   -> 200 {"id": 1, "email": "dev@x.io", "name": "Dev"}
GET /users/99  -> 404 {"detail": "User not found"}
```

Do **not** delete `password_hash` by hand — let `response_model` do it.
