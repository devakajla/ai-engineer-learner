from datetime import datetime
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import DateTime, String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbSession = Annotated[Session, Depends(get_db)]


class NoteIn(BaseModel):
    text: str = Field(min_length=1, max_length=500)


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    created_at: datetime


app = FastAPI()


@app.post("/notes", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(payload: NoteIn, db: DbSession):
    note = Note(text=payload.text)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@app.get("/notes/{note_id}", response_model=NoteOut)
def get_note(note_id: int, db: DbSession):
    note = db.get(Note, note_id)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


@app.get("/notes", response_model=list[NoteOut])
def list_notes(db: DbSession):
    return db.scalars(select(Note).order_by(Note.id.desc())).all()
