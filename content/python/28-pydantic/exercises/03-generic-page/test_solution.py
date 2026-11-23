import pytest
from pydantic import ValidationError

from solution import Page, Product, paginate, parse_products


def test_generic_validation():
    page = Page[Product].model_validate({"items": [{"name": "Pen", "price": 5}], "total": 3, "limit": 1, "offset": 0})
    assert isinstance(page.items[0], Product) and page.has_more is True
    with pytest.raises(ValidationError):
        Page[Product].model_validate({"items": [{"name": "Bad", "price": -1}], "total": 1, "limit": 1, "offset": 0})
    with pytest.raises(ValidationError):
        Page[int].model_validate({"items": [1], "total": 1, "limit": 500, "offset": 0})


def test_paginate():
    p = paginate([1, 2, 3, 4, 5], limit=2, offset=2)
    assert p.items == [3, 4] and p.total == 5 and p.has_more is True
    last = paginate([1, 2, 3, 4, 5], limit=2, offset=4)
    assert last.items == [5] and last.has_more is False
    assert "has_more" in last.model_dump()


def test_parse_products():
    products = parse_products(b'[{"name": "a", "price": 1}, {"name": "b", "price": 2.5}]')
    assert [p.name for p in products] == ["a", "b"]
    with pytest.raises(ValidationError):
        parse_products('[{"name": "a"}]')
