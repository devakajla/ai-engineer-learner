from typing import Annotated, Literal

from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI()

CATEGORIES = ["books", "games", "music"]
PRODUCTS = [
    {"id": i, "name": f"Item {i:02d}", "category": CATEGORIES[i % 3], "price": float((i * 37) % 50)}
    for i in range(1, 58)
]


@app.get("/products")
def list_products(limit: int = 10, offset: int = 0):
    return PRODUCTS[offset : offset + limit]
