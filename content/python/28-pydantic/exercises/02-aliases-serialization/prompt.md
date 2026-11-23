# Talk camelCase, think snake_case

A payment provider sends JSON like:

```json
{"orderId": 42, "customerEmail": "dev@x.io", "lineItems": [{"sku": "A1", "unitPrice": 10.0, "qty": 2}], "couponCode": null}
```

Write models `LineItem` (`sku`, `unit_price`, `qty`) and `Order` (`order_id`, `customer_email`, `line_items`, `coupon_code: str | None = None`) that:

- parse the camelCase JSON (use `alias_generator=to_camel` + `populate_by_name=True` on **both** models)
- have a `@computed_field` `total` = sum of `unit_price * qty`, rounded to 2 decimals
- `Order.to_api()` returns a camelCase dict **without `None` values** (include `total`)

```python
o = Order.model_validate_json(raw)
o.order_id         # -> 42
o.to_api()         # -> {"orderId": 42, "customerEmail": "dev@x.io", "lineItems": [{"sku": "A1", "unitPrice": 10.0, "qty": 2}], "total": 20.0}
```
