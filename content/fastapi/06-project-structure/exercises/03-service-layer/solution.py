from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel


# ---- repository (storage only) ----
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


# ---- service (business rules) ----
class NoteNotFoundError(Exception):
    pass


class DuplicateNoteError(Exception):
    pass


class NoteService:
    def __init__(self, repo: InMemoryNoteRepository) -> None:
        self.repo = repo

    def create(self, title: str) -> dict:
        if any(n["title"].lower() == title.lower() for n in self.repo.list()):
            raise DuplicateNoteError(title)
        return self.repo.add(title)

    def get(self, note_id: int) -> dict:
        note = self.repo.get(note_id)
        if note is None:
            raise NoteNotFoundError(note_id)
        return note


# ---- routes (HTTP) ----
class NoteCreate(BaseModel):
    title: str


app = FastAPI()
service = NoteService(InMemoryNoteRepository())


@app.post("/notes", status_code=status.HTTP_201_CREATED)
def create_note(payload: NoteCreate):
    try:
        return service.create(payload.title)
    except DuplicateNoteError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Note already exists")


@app.get("/notes/{note_id}")
def get_note(note_id: int):
    try:
        return service.get(note_id)
    except NoteNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Note not found")
