from sqlalchemy import ForeignKey, String, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, selectinload


class Base(DeclarativeBase):
    pass


def book_counts(session):
    authors = session.scalars(select(Author).order_by(Author.name)).all()
    return [(a.name, len(a.books)) for a in authors]   # N+1!
