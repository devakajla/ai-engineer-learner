# Create a user

Create a Pydantic model `UserCreate` and a route `POST /users`.

`UserCreate` fields:

| Field | Type | Rules |
|---|---|---|
| `name` | str | 1–50 chars, surrounding spaces stripped |
| `email` | str | must contain `@` (use `pattern=r".+@.+"`) |
| `age` | int | 13–120 |
| `bio` | str or None | optional, default `None`, max 200 chars |

The route returns the validated user plus `"id": 1`:

```text
POST /users {"name": " Dev ", "email": "dev@x.io", "age": 22}
-> 200 {"id": 1, "name": "Dev", "email": "dev@x.io", "age": 22, "bio": null}
```

Unknown fields (e.g. `"is_admin": true`) must be **rejected** with 422.
