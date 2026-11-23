from typing import Annotated

from fastapi import Depends, FastAPI, status
from pydantic import BaseModel

app = FastAPI()


class CommentIn(BaseModel):
    author: str
    text: str


class EmailNotifier:
    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []

    def send(self, to: str, message: str) -> None:
        self.sent.append((to, message))


_notifier = EmailNotifier()


def get_notifier() -> EmailNotifier:
    return _notifier


NotifierDep = Annotated[EmailNotifier, Depends(get_notifier)]

_comments: list[dict] = []


@app.post("/comments", status_code=status.HTTP_201_CREATED)
def create_comment(payload: CommentIn, notifier: NotifierDep):
    comment = {"id": len(_comments) + 1, **payload.model_dump()}
    _comments.append(comment)
    notifier.send(payload.author, "Thanks for your comment")
    return comment
