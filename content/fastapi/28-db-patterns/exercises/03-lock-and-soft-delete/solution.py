from sqlalchemy import String, select, update
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class StaleVersion(Exception):
    pass


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    version: Mapped[int] = mapped_column(default=1)
    deleted: Mapped[bool] = mapped_column(default=False)


def add_note(session: Session, title: str) -> Note:
    note = Note(title=title)
    session.add(note)
    session.commit()
    session.refresh(note)
    return note


def update_title(session: Session, note_id: int, expected_version: int, title: str) -> Note:
    result = session.execute(
        update(Note)
        .where(Note.id == note_id, Note.version == expected_version, Note.deleted.is_(False))
        .values(title=title, version=Note.version + 1)
    )
    session.commit()
    if result.rowcount == 0:
        note = session.get(Note, note_id)
        if note is None or note.deleted:
            raise LookupError("note not found")
        raise StaleVersion(f"note is at version {note.version}, not {expected_version}")
    note = session.get(Note, note_id)
    session.refresh(note)
    return note


def soft_delete(session: Session, note_id: int) -> bool:
    note = session.get(Note, note_id)
    if note is None or note.deleted:
        return False
    note.deleted = True
    session.commit()
    return True


def list_notes(session: Session) -> list[Note]:
    return list(session.scalars(select(Note).where(Note.deleted.is_(False)).order_by(Note.id)))
