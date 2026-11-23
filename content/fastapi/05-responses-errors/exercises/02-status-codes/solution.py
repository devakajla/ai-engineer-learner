from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

BOOKMARKS: dict[int, dict] = {}


class BookmarkCreate(BaseModel):
    url: str
    title: str


@app.post("/bookmarks", status_code=status.HTTP_201_CREATED)
def create_bookmark(payload: BookmarkCreate):
    if any(b["url"] == payload.url for b in BOOKMARKS.values()):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Bookmark already exists")
    bookmark_id = max(BOOKMARKS, default=0) + 1
    BOOKMARKS[bookmark_id] = {"id": bookmark_id, **payload.model_dump()}
    return BOOKMARKS[bookmark_id]


@app.delete("/bookmarks/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bookmark(bookmark_id: int) -> None:
    if bookmark_id not in BOOKMARKS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")
    del BOOKMARKS[bookmark_id]
