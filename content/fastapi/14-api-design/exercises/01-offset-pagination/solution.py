from typing import Annotated, Literal

from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI()

CATEGORIES = ["books", "games", "music"]
PRODUCTS = [
    {"id": i, "name": f"Item {i:02d}", "category": CATEGORIES[i % 3], "price": float((i * 37) % 50)}
    for i in range(1, 58)
]


class Product(BaseModel):
    id: int
    name: str
    category: str
    price: float


class Page[T](BaseModel):
    items: list[T]
    total: int
    limit: int
    offset: int


SortField = Literal["id", "-id", "price", "-price", "name", "-name"]


@app.get("/products", response_model=Page[Product])
def list_products(
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
    category: str | None = None,
    q: str | None = None,
    sort: SortField = "id",
):
    items = PRODUCTS
    if category is not None:
        items = [p for p in items if p["category"] == category]
    if q:
        needle = q.lower()
        items = [p for p in items if needle in p["name"].lower()]
    field = sort.lstrip("-")
    descending = sort.startswith("-")
    items = sorted(items, key=lambda p: p["id"])                 # tie-breaker first (stable sort)
    items = sorted(items, key=lambda p: p[field], reverse=descending)
    return {"items": items[offset : offset + limit], "total": len(items), "limit": limit, "offset": offset}
