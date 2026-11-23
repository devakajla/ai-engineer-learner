# A reusable pagination dependency

Write a dependency `pagination(limit, offset)`:

- `limit`: int, default 20, 1–100
- `offset`: int, default 0, ≥ 0
- returns a `Page` dataclass/object with `limit` and `offset`

Make an alias `PaginationDep = Annotated[Page, Depends(pagination)]` and use it in **two** routes over the provided lists:

- `GET /items` → `ITEMS[offset : offset + limit]`
- `GET /users` → `USERS[offset : offset + limit]`

Both must reject `limit=0`, `limit=101`, `offset=-1` with 422.
