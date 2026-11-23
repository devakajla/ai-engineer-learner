"""The app you are testing. Do not edit it."""

import os

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, Field

MUTANT = os.environ.get("MUTANT", "")


class NoteRepo:
    def __init__(self) -> None:
        self.notes: dict[int, dict] = {}
        self.next_id = 1

    def add(self, text: str, pinned: bool) -> dict:
        note = {"id": self.next_id, "text": text, "pinned": pinned}
        self.notes[note["id"]] = note
        self.next_id += 1
        return note


_shared_repo = NoteRepo()


def get_repo() -> NoteRepo:
    return _shared_repo


class NoteIn(BaseModel):
    text: str = Field(min_length=1)
    pinned: bool = False


class NotePatch(BaseModel):
    text: str | None = Field(default=None, min_length=1)
    pinned: bool | None = None


app = FastAPI()


@app.post("/notes", status_code=200 if MUTANT == "create_status" else status.HTTP_201_CREATED)
def create(payload: NoteIn, repo: NoteRepo = Depends(get_repo)):
    return repo.add(payload.text, payload.pinned)


@app.get("/notes")
def list_notes(repo: NoteRepo = Depends(get_repo)):
    notes = list(repo.notes.values())
    if MUTANT != "pinned_first":
        notes.sort(key=lambda n: (not n["pinned"], n["id"]))
    return notes


@app.patch("/notes/{note_id}")
def patch(note_id: int, payload: NotePatch, repo: NoteRepo = Depends(get_repo)):
    note = repo.notes.get(note_id)
    if note is None:
        raise HTTPException(404, "Note not found")
    changes = payload.model_dump() if MUTANT == "patch_overwrites" else payload.model_dump(exclude_unset=True)
    note.update(changes)
    return note


@app.delete("/notes/{note_id}", status_code=204)
def delete(note_id: int, repo: NoteRepo = Depends(get_repo)):
    if note_id not in repo.notes:
        raise HTTPException(404, "Note not found")
    if MUTANT != "delete_noop":
        del repo.notes[note_id]
