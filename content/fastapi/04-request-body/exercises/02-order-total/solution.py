from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class Item(BaseModel):
    name: str
    quantity: int = Field(ge=1)
    unit_price: float = Field(gt=0)


class Order(BaseModel):
    customer: str
    items: list[Item] = Field(min_length=1)


@app.post("/orders")
def create_order(order: Order):
    total = sum(i.quantity * i.unit_price for i in order.items)
    return {"customer": order.customer, "item_count": len(order.items), "total": round(total, 2)}
