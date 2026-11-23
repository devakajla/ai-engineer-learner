# Order total with nested models

Create models `Item` (`name`: str, `quantity`: int ≥ 1, `unit_price`: float > 0) and `Order` (`customer`: str, `items`: list of `Item` with **at least one** item).

`POST /orders` returns:

```json
{"customer": "Dev", "item_count": 2, "total": 250.0}
```

where `item_count` is the number of items in the list and `total` is the sum of `quantity * unit_price`, **rounded to 2 decimals**.

```text
POST /orders {"customer": "Dev", "items": [{"name": "pen", "quantity": 2, "unit_price": 25},
                                           {"name": "book", "quantity": 1, "unit_price": 200}]}
-> {"customer": "Dev", "item_count": 2, "total": 250.0}
```

An empty `items` list, `quantity: 0` or a negative price → 422.
