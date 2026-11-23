from solution import LineItem, Order

RAW = '{"orderId": 42, "customerEmail": "dev@x.io", "lineItems": [{"sku": "A1", "unitPrice": 10.0, "qty": 2}], "couponCode": null}'


def test_parse_camel():
    o = Order.model_validate_json(RAW)
    assert o.order_id == 42 and o.customer_email == "dev@x.io"
    assert o.line_items[0].unit_price == 10.0


def test_populate_by_name():
    o = Order(order_id=1, customer_email="a@b.c", line_items=[LineItem(sku="x", unit_price=1.5, qty=3)])
    assert o.total == 4.5


def test_to_api():
    assert Order.model_validate_json(RAW).to_api() == {
        "orderId": 42,
        "customerEmail": "dev@x.io",
        "lineItems": [{"sku": "A1", "unitPrice": 10.0, "qty": 2}],
        "total": 20.0,
    }


def test_coupon_kept_when_present():
    o = Order.model_validate({"orderId": 1, "customerEmail": "a@b.c", "lineItems": [], "couponCode": "SAVE"})
    assert o.to_api()["couponCode"] == "SAVE" and o.to_api()["total"] == 0
