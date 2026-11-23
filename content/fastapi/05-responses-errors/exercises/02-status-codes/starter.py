from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

BOOKMARKS: dict[int, dict] = {}


class BookmarkCreate(BaseModel):
    url: str
    title: str
