from typing import Literal

from pydantic import BaseModel


class Answer(BaseModel):
    """The shape of every answer Copilot gives back."""

    answer: str
    found: bool
    confidence: Literal["high", "medium", "low"]
    quote: str = ""
