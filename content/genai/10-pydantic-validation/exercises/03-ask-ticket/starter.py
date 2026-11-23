from pydantic import BaseModel, Field, ValidationError


class Ticket(BaseModel):
    title: str = Field(min_length=1)
    priority: int = Field(ge=1, le=5)
    tags: list[str] = []


def ask_ticket(client, text, max_tries=3):
    pass
