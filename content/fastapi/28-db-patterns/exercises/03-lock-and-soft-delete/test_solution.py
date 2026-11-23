import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from solution import Base, Note, StaleVersion, add_note, list_notes, soft_delete, update_title


@pytest.fixture
def engine():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    with Session(engine) as s:
        yield s


def test_new_note_starts_at_version_1(session):
    n = add_note(session, "draft")
    assert n.version == 1 and n.deleted is False


def test_update_bumps_version(session):
    n = add_note(session, "draft")
    updated = update_title(session, n.id, 1, "better")
    assert updated.title == "better" and updated.version == 2
    assert update_title(session, n.id, 2, "best").version == 3


def test_stale_update_is_rejected_and_changes_nothing(session):
    n = add_note(session, "draft")
    update_title(session, n.id, 1, "from A")
    with pytest.raises(StaleVersion):
        update_title(session, n.id, 1, "from B")
    session.expire_all()
    fresh = session.get(Note, n.id)
    assert fresh.title == "from A" and fresh.version == 2


def test_two_sessions_two_editors(engine):
    with Session(engine) as setup:
        note_id = add_note(setup, "shared").id
    with Session(engine) as a, Session(engine) as b:
        seen_a = a.get(Note, note_id).version
        seen_b = b.get(Note, note_id).version
        update_title(a, note_id, seen_a, "A wins")
        with pytest.raises(StaleVersion):
            update_title(b, note_id, seen_b, "B loses")
    with Session(engine) as check:
        assert check.get(Note, note_id).title == "A wins"


def test_future_version_is_also_stale(session):
    n = add_note(session, "x")
    with pytest.raises(StaleVersion):
        update_title(session, n.id, 5, "y")


def test_missing_note(session):
    with pytest.raises(LookupError):
        update_title(session, 999, 1, "x")


def test_soft_delete_keeps_row(session):
    a, b = add_note(session, "a"), add_note(session, "b")
    assert soft_delete(session, a.id) is True
    assert soft_delete(session, a.id) is False
    assert soft_delete(session, 999) is False
    assert [n.title for n in list_notes(session)] == ["b"]
    assert session.scalar(select(func.count()).select_from(Note)) == 2, "the row must stay in the table"


def test_update_deleted_note_is_not_found(session):
    n = add_note(session, "a")
    soft_delete(session, n.id)
    with pytest.raises(LookupError):
        update_title(session, n.id, 1, "zombie")


def test_list_is_ordered_by_id(session):
    ids = [add_note(session, t).id for t in "cab"]
    assert [n.id for n in list_notes(session)] == ids
