from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, Response, status
from pydantic import BaseModel, Field

app = FastAPI()

NOTES: dict[int, dict] = {}


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    body: str = ""


class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    body: str | None = None


def _get_or_404(note_id: int) -> dict:
    note = NOTES.get(note_id)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


@app.post("/notes", status_code=status.HTTP_201_CREATED)
def create_note(payload: NoteCreate):
    note_id = max(NOTES, default=0) + 1
    note = {"id": note_id, **payload.model_dump()}
    NOTES[note_id] = note
    return note


@app.get("/notes")
def list_notes(
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    notes = [NOTES[i] for i in sorted(NOTES)]
    return notes[offset : offset + limit]


@app.get("/notes/{note_id}")
def get_note(note_id: int):
    return _get_or_404(note_id)


@app.patch("/notes/{note_id}")
def update_note(note_id: int, payload: NoteUpdate):
    note = _get_or_404(note_id)
    note.update(payload.model_dump(exclude_unset=True))
    return note


@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int):
    _get_or_404(note_id)
    del NOTES[note_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)
