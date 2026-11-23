# Global exception handlers

The starter has domain errors and a service. **Routes must not use try/except.** Register handlers so that:

| Raised | Status | Body |
|---|---|---|
| `NotFoundError(msg)` | 404 | `{"detail": msg, "code": "not_found"}` |
| `ConflictError(msg)` | 409 | `{"detail": msg, "code": "conflict"}` |
| any other `AppError` | 400 | `{"detail": msg, "code": "app_error"}` |
| any unexpected `Exception` | 500 | `{"detail": "Internal server error", "code": "internal_error"}` (no exception text!) |

Keep the status mapping in a dict in the API code (`STATUS_FOR`), not in the error classes.

Routes (given, don't add try/except):
- `GET /users/{user_id}` → 404 for unknown ids
- `POST /users?email=...` → 409 for duplicate emails
- `GET /boom` → raises `RuntimeError("secret db password")`
