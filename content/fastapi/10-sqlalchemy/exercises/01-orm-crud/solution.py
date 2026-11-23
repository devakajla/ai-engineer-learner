from sqlalchemy import Boolean, String, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    author: Mapped[str] = mapped_column(String(100))
    year: Mapped[int | None]
    available: Mapped[bool] = mapped_column(Boolean, default=True, index=True)


def add_book(session: Session, title: str, author: str, year: int | None = None) -> Book:
    book = Book(title=title, author=author, year=year)
    session.add(book)
    session.commit()
    session.refresh(book)
    return book


def available_by(session: Session, author: str) -> list[Book]:
    stmt = (
        select(Book)
        .where(Book.author == author, Book.available.is_(True))
        .order_by(Book.year, Book.title)
    )
    return list(session.scalars(stmt))


def checkout(session: Session, book_id: int) -> bool:
    book = session.get(Book, book_id)
    if book is None or not book.available:
        return False
    book.available = False
    session.commit()
    return True


def count_available(session: Session) -> int:
    return session.scalar(select(func.count()).select_from(Book).where(Book.available.is_(True)))
