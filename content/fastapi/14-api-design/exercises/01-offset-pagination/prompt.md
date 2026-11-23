# Offset pagination with filtering and sorting

`PRODUCTS` (given) is a list of 57 dicts `{"id", "name", "category", "price"}`.

Build `GET /products` returning a `Page[Product]` envelope `{"items", "total", "limit", "offset"}`:

| param | rules |
|---|---|
| `limit` | 1–50, default 10 |
| `offset` | ≥ 0, default 0 |
| `category` | optional exact filter |
| `q` | optional, case-insensitive substring of `name` |
| `sort` | one of `id`, `-id`, `price`, `-price`, `name`, `-name` (default `id`); anything else → 422 |

- `total` = number of items **after filtering**, before paging.
- Sorting must be deterministic: break ties by `id`.
- Use a generic `Page[T]` Pydantic model and a `Product` model.
