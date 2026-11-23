from enum import Enum
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, status

app = FastAPI()

PRODUCTS = [
    {"id": 1, "name": "Keyboard", "category": "accessories", "price": 49.0},
    {"id": 2, "name": "Mouse", "category": "accessories", "price": 25.5},
    {"id": 3, "name": "Monitor", "category": "displays", "price": 199.0},
    {"id": 4, "name": "Laptop", "category": "computers", "price": 899.0},
    {"id": 5, "name": "Webcam", "category": "accessories", "price": 59.0},
    {"id": 6, "name": "Tablet", "category": "computers", "price": 329.0},
]


class Sort(str, Enum):
    name = "name"
    price = "price"
    price_desc = "-price"


@app.get("/products")
def search_products(
    category: str | None = None,
    min_price: Annotated[float | None, Query(ge=0)] = None,
    max_price: Annotated[float | None, Query(ge=0)] = None,
    sort: Sort = Sort.name,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_price cannot be greater than max_price",
        )
    items = PRODUCTS
    if category is not None:
        items = [p for p in items if p["category"].lower() == category.lower()]
    if min_price is not None:
        items = [p for p in items if p["price"] >= min_price]
    if max_price is not None:
        items = [p for p in items if p["price"] <= max_price]
    if sort is Sort.name:
        items = sorted(items, key=lambda p: p["name"].lower())
    else:
        items = sorted(items, key=lambda p: p["price"], reverse=sort is Sort.price_desc)
    return {"total": len(items), "items": items[offset : offset + limit]}


@app.get("/products/{product_id}")
def get_product(product_id: int):
    for product in PRODUCTS:
        if product["id"] == product_id:
            return product
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
