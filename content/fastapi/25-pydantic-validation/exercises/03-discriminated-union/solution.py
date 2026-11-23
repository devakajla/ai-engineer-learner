from typing import Annotated, Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class Email(BaseModel):
    channel: Literal["email"]
    to: str = Field(pattern=r".+@.+")
    subject: str = Field(min_length=1, max_length=100)


class Sms(BaseModel):
    channel: Literal["sms"]
    phone: str = Field(pattern=r"^\d{10}$")


class Push(BaseModel):
    channel: Literal["push"]
    device_id: str = Field(min_length=1)


Message = Annotated[Email | Sms | Push, Field(discriminator="channel")]


@app.post("/notify")
def notify(message: Message):
    if isinstance(message, Email):
        target = message.to
    elif isinstance(message, Sms):
        target = message.phone
    else:
        target = message.device_id
    return {"sent_via": message.channel, "target": target}
