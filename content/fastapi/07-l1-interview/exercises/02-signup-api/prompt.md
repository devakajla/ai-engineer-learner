# Interview task: Signup API (25 min)

Build a small user API. Store users in the module-level list `USERS: list[dict]`. A new id is `max((u["id"] for u in USERS), default=0) + 1`.

| Endpoint | Behaviour |
|---|---|
| `POST /users` body `{"email", "password", "name"}` | **201** with `{"id", "email", "name"}`. **Never** return the password |
| `GET /users/{user_id}` | `{"id", "email", "name"}`, or **404** `{"detail": "User not found"}` |

Rules for `POST /users`:

- `email` must look like an email: something, `@`, something, `.`, something (else 422). Store it **lower-cased**.
- `password` is at least 8 characters, `name` is 1-50 characters (else 422).
- **Unknown fields are rejected** with 422 (for example `"is_admin": true`).
- If the email is already registered (compare case-insensitively) → **409** `{"detail": "Email already registered"}`.

Keep the password in `USERS` (hashing comes in the auth lessons), but make sure no endpoint can leak it.

Be ready to discuss: mass assignment, why 409 and not 400, race conditions on "check then insert" and the unique index that fixes them.
