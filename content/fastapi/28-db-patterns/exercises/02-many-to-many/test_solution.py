import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from solution import (
    Base,
    add_course,
    add_student,
    courses_of,
    enroll,
    popularity,
    students_in,
)


@pytest.fixture
def session():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


def test_link_table_has_composite_primary_key():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    insp = inspect(engine)
    assert "enrollments" in insp.get_table_names(), "the link table must be called enrollments"
    pk = insp.get_pk_constraint("enrollments")["constrained_columns"]
    assert set(pk) == {"student_id", "course_id"}, "both columns together are the primary key"


def test_enroll_and_read_both_sides(session):
    ann, bob = add_student(session, "Ann"), add_student(session, "Bob")
    py, db = add_course(session, "Python"), add_course(session, "Databases")
    assert enroll(session, ann.id, py.id) is True
    assert enroll(session, ann.id, db.id) is True
    assert enroll(session, bob.id, py.id) is True
    assert courses_of(session, ann.id) == ["Databases", "Python"]
    assert courses_of(session, bob.id) == ["Python"]
    assert students_in(session, py.id) == ["Ann", "Bob"]
    assert students_in(session, db.id) == ["Ann"]


def test_enroll_twice_is_false_and_stored_once(session):
    ann, py = add_student(session, "Ann"), add_course(session, "Python")
    assert enroll(session, ann.id, py.id) is True
    assert enroll(session, ann.id, py.id) is False
    assert courses_of(session, ann.id) == ["Python"]
    assert students_in(session, py.id) == ["Ann"]


def test_missing_ids(session):
    ann, py = add_student(session, "Ann"), add_course(session, "Python")
    with pytest.raises(LookupError):
        enroll(session, 999, py.id)
    with pytest.raises(LookupError):
        enroll(session, ann.id, 999)
    with pytest.raises(LookupError):
        courses_of(session, 999)
    with pytest.raises(LookupError):
        students_in(session, 999)


def test_empty_lists(session):
    ann, py = add_student(session, "Ann"), add_course(session, "Python")
    assert courses_of(session, ann.id) == []
    assert students_in(session, py.id) == []


def test_popularity_order_and_zero(session):
    students = [add_student(session, n) for n in ("A", "B", "C")]
    py, db, ml, go = (add_course(session, t) for t in ("Python", "Databases", "ML", "Go"))
    for s in students:
        enroll(session, s.id, py.id)
    enroll(session, students[0].id, db.id)
    enroll(session, students[1].id, db.id)
    enroll(session, students[0].id, ml.id)
    assert popularity(session) == [("Python", 3), ("Databases", 2), ("ML", 1), ("Go", 0)]


def test_popularity_ties_by_title(session):
    s = add_student(session, "A")
    b, a = add_course(session, "B"), add_course(session, "A")
    enroll(session, s.id, b.id)
    enroll(session, s.id, a.id)
    assert popularity(session) == [("A", 1), ("B", 1)]
