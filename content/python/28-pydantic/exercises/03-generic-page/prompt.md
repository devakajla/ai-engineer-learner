# A generic paginated response

Write:

1. A generic model `Page[T]` with `items: list[T]`, `total: int (≥ 0)`, `limit: int (1–100)`, `offset: int (≥ 0)`, plus a `@computed_field` `has_more` = `offset + len(items) < total`.
2. A model `Product` (`name: str`, `price: float > 0`).
3. `paginate(items, limit, offset) -> Page[...]` — a generic function that slices any list and returns a `Page` of the same item type.
4. `parse_products(raw_json: str | bytes) -> list[Product]` using a `TypeAdapter`.

```python
page = Page[Product].model_validate({"items": [{"name": "Pen", "price": 5}], "total": 3, "limit": 1, "offset": 0})
page.has_more    # -> True
paginate([1, 2, 3, 4, 5], limit=2, offset=2).items   # -> [3, 4]
```
