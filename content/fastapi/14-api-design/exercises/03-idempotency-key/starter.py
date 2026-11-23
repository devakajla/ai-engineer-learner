from typing import Annotated

from fastapi import FastAPI, Header, HTTPException, Response, status
from pydantic import BaseModel, Field

app = FastAPI()

PAYMENTS: list[dict] = []
IDEMPOTENCY_STORE: dict[str, dict] = {}


class PaymentIn(BaseModel):
    amount: int = Field(gt=0)
    currency: str


@app.post("/payments", status_code=201)
def create_payment(payload: PaymentIn):
    payment = {"id": len(PAYMENTS) + 1, **payload.model_dump()}
    PAYMENTS.append(payment)
    return payment
