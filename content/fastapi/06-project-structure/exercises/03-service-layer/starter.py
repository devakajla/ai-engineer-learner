from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel


# ---- repository (storage only) — given ----
class InMemoryNoteRepository:
    def __init__(self) -> None:
        self._notes: dict[int, dict] = {}
        self._next_id = 1

    def list(self) -> list[dict]:
        return list(self._notes.values())

    def get(self, note_id: int) -> dict | None:
        return self._notes.get(note_id)

    def add(self, title: str) -> dict:
        note = {"id": self._next_id, "title": title}
        self._notes[note["id"]] = note
        self._next_id += 1
        return note


# ---- service (business rules) — write it ----
class NoteNotFoundError(Exception):
    pass


class DuplicateNoteError(Exception):
    pass


class NoteService:
    ...


# ---- routes (HTTP) — write them ----
class NoteCreate(BaseModel):
    title: str


app = FastAPI()
