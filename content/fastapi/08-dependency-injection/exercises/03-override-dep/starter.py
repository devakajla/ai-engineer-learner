from typing import Annotated

from fastapi import Depends, FastAPI, status
from pydantic import BaseModel

app = FastAPI()


class CommentIn(BaseModel):
    author: str
    text: str
