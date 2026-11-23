from typing import Annotated

from fastapi import FastAPI, Path
from pydantic import BaseModel, Field

app = FastAPI()


class NoteUpdate(BaseModel):
    text: str = Field(min_length=1, max_length=500)
    pinned: bool = False


@app.put("/notes/{note_id}")
def replace_note(note_id: Annotated[int, Path(ge=1)], note: NoteUpdate, notify: bool = False):
    return {"note_id": note_id, "notify": notify, "note": note.model_dump()}
