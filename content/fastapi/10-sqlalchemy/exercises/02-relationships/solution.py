from sqlalchemy import ForeignKey, String, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, selectinload


class Base(DeclarativeBase):
    pass


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    books: Mapped[list["Book"]] = relationship(back_populates="author")


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    author: Mapped[Author] = relationship(back_populates="books")


def book_counts(session: Session) -> list[tuple[str, int]]:
    authors = session.scalars(select(Author).options(selectinload(Author.books)).order_by(Author.name)).all()
    return [(a.name, len(a.books)) for a in authors]
