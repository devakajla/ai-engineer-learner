# Routers and versioning

Create an `APIRouter` named `router` for users, with **prefix `/users`** and **tag `users`**:

- `GET ""` → `[]`  (the collection)
- `GET "/{user_id}"` → `{"id": <user_id>}` (int)

Then create `app` and include the router under **`/api/v1`**, so the final paths are:

```text
GET /api/v1/users       -> []
GET /api/v1/users/7     -> {"id": 7}
GET /users              -> 404   (only the versioned path exists)
```

Set `prefix` and `tags` on the router — not on each route.
