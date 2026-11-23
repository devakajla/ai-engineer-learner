"""The app you are testing. Do not edit it — write tests in your solution file.

(The checker sets the MUTANT environment variable to inject bugs and expects your tests to catch them.)
"""

import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

MUTANT = os.environ.get("MUTANT", "")

app = FastAPI()


class Item(BaseModel):
    price: float = Field(gt=0)
    qty: int = Field(ge=1)


class QuoteIn(BaseModel):
    items: list[Item] = Field(min_length=1)
    coupon: str | None = None


COUPONS = {"SAVE10": 0.05 if MUTANT == "coupon_rate" else 0.10}
BULK_THRESHOLD = 1000
BULK_DISCOUNT = 50


@app.post("/quote")
def quote(payload: QuoteIn):
    subtotal = sum(i.price * (1 if MUTANT == "qty" else i.qty) for i in payload.items)
    discount = 0.0
    if payload.coupon is not None:
        if payload.coupon not in COUPONS:
            if MUTANT != "unknown_coupon":
                raise HTTPException(status_code=400, detail="Invalid coupon")
        else:
            discount += subtotal * COUPONS[payload.coupon]
    bulk = subtotal > BULK_THRESHOLD if MUTANT == "bulk_threshold" else subtotal >= BULK_THRESHOLD
    if bulk:
        discount += BULK_DISCOUNT
    total = subtotal - discount
    if MUTANT != "rounding":
        subtotal, discount, total = round(subtotal, 2), round(discount, 2), round(total, 2)
    return {"subtotal": subtotal, "discount": discount, "total": total}
