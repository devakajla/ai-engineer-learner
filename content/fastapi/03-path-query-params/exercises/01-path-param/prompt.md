# Users by id

Create `app` with:

- `GET /users/me` → `{"user_id": "me"}`
- `GET /users/{user_id}` → `{"user_id": <int>}` where `user_id` must be an int **≥ 1**

```text
GET /users/7    -> 200 {"user_id": 7}
GET /users/me   -> 200 {"user_id": "me"}
GET /users/0    -> 422
GET /users/abc  -> 422
```

Think about route order.
