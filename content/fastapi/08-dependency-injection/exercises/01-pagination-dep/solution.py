from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, FastAPI, Query

app = FastAPI()

ITEMS = [f"item-{i}" for i in range(50)]
USERS = [f"user-{i}" for i in range(30)]


@dataclass
class Page:
    limit: int
    offset: int


def pagination(
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Page:
    return Page(limit=limit, offset=offset)


PaginationDep = Annotated[Page, Depends(pagination)]


@app.get("/items")
def list_items(page: PaginationDep):
    return ITEMS[page.offset : page.offset + page.limit]


@app.get("/users")
def list_users(page: PaginationDep):
    return USERS[page.offset : page.offset + page.limit]
