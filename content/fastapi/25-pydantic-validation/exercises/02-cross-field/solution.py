from datetime import date

from fastapi import FastAPI
from pydantic import BaseModel, Field, computed_field, model_validator

app = FastAPI()


class BookingIn(BaseModel):
    guest: str = Field(min_length=1, max_length=50)
    check_in: date
    check_out: date
    rooms: int = Field(default=1, ge=1, le=5)

    @model_validator(mode="after")
    def dates_in_order(self):
        if self.check_out <= self.check_in:
            raise ValueError("check_out must be after check_in")
        return self


class BookingOut(BookingIn):
    @computed_field
    @property
    def nights(self) -> int:
        return (self.check_out - self.check_in).days


@app.post("/bookings", status_code=201, response_model=BookingOut)
def create_booking(payload: BookingIn):
    return BookingOut(**payload.model_dump())
