from typing import Annotated

from fastapi import FastAPI, Header, HTTPException, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI()

PAYMENTS: list[dict] = []
IDEMPOTENCY_STORE: dict[str, dict] = {}


class PaymentIn(BaseModel):
    amount: int = Field(gt=0)
    currency: str


@app.post("/payments", status_code=status.HTTP_201_CREATED)
def create_payment(payload: PaymentIn, idempotency_key: Annotated[str | None, Header()] = None):
    request_body = payload.model_dump()
    if idempotency_key is not None and idempotency_key in IDEMPOTENCY_STORE:
        saved = IDEMPOTENCY_STORE[idempotency_key]
        if saved["request"] != request_body:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Idempotency-Key reused with a different request",
            )
        return JSONResponse(
            status_code=saved["status"], content=saved["response"], headers={"Idempotent-Replayed": "true"}
        )

    payment = {"id": len(PAYMENTS) + 1, **request_body}
    PAYMENTS.append(payment)
    if idempotency_key is not None:
        IDEMPOTENCY_STORE[idempotency_key] = {
            "request": request_body,
            "status": status.HTTP_201_CREATED,
            "response": payment,
        }
    return payment
