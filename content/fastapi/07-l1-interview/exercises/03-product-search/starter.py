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
