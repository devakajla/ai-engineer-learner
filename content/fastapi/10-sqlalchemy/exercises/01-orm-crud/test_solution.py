import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from solution import Base, Book, add_book, available_by, checkout, count_available


@pytest.fixture
def session():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


def test_schema():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    cols = {c["name"]: c for c in inspect(engine).get_columns("books")}
    assert set(cols) == {"id", "title", "author", "year", "available"}
    assert cols["year"]["nullable"] is True and cols["title"]["nullable"] is False
    assert any("available" in ix["column_names"] for ix in inspect(engine).get_indexes("books"))


def test_add_and_query(session):
    b = add_book(session, "Fluent Python", "Ramalho", 2022)
    assert b.id and b.available is True
    add_book(session, "Old one", "Ramalho", 2015)
    add_book(session, "Other", "Someone")
    assert [x.title for x in available_by(session, "Ramalho")] == ["Old one", "Fluent Python"]


def test_checkout_and_count(session):
    a = add_book(session, "A", "x")
    add_book(session, "B", "x")
    assert count_available(session) == 2
    assert checkout(session, a.id) is True
    assert checkout(session, a.id) is False
    assert checkout(session, 999) is False
    assert count_available(session) == 1
    assert [b.title for b in available_by(session, "x")] == ["B"]


def test_title_required(session):
    session.add(Book(author="x"))
    with pytest.raises(IntegrityError):
        session.commit()
