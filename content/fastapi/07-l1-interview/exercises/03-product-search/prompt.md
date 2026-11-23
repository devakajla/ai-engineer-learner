# Interview task: Product search (25 min)

`PRODUCTS` (a list of dicts with `id`, `name`, `category`, `price`) is already in the file. Add:

**`GET /products`** with these query parameters:

| Param | Meaning |
|---|---|
| `category` | optional; match case-insensitively |
| `min_price`, `max_price` | optional floats, both `>= 0`; keep products with `min_price <= price <= max_price` |
| `sort` | one of `name`, `price`, `-price` (descending price); default `name`. Anything else → 422. Sort names ignoring case |
| `limit` | 1-100, default 10 |
| `offset` | `>= 0`, default 0 |

Response: `{"total": <count after filtering, before paging>, "items": [<page of products>]}`.
If `min_price > max_price` → **400** `{"detail": "min_price cannot be greater than max_price"}`.

**`GET /products/{product_id}`** → the product, or **404** `{"detail": "Product not found"}`.

Use an `Enum` for `sort` and `Annotated[..., Query(...)]` for the limits.

Be ready to discuss: why `total` is useful, offset vs cursor pagination, what index you would add if this was SQL.
