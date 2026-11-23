from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from solution import Author, Base, Book, book_counts


def setup_db():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    session = Session(engine)
    for i in range(20):
        a = Author(name=f"author{i:02d}")
        a.books = [Book(title=f"b{i}-{j}") for j in range(i % 3)]
        session.add(a)
    session.commit()
    session.expunge_all()
    return engine, session


def test_relationship():
    engine, session = setup_db()
    book = session.query(Book).first()
    assert book.author.name.startswith("author")
    assert book in book.author.books


def test_counts_and_query_budget():
    engine, session = setup_db()
    statements = []
    event.listen(engine, "before_cursor_execute", lambda *a: statements.append(a[2]))
    result = book_counts(session)
    assert result[:4] == [("author00", 0), ("author01", 1), ("author02", 2), ("author03", 0)]
    assert len(result) == 20
    assert len(statements) <= 2, f"N+1 detected: {len(statements)} queries (use selectinload or GROUP BY)"
