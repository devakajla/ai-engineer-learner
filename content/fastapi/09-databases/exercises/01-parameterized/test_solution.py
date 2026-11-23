import inspect
import sqlite3

import solution
from solution import add_note, create_schema, get_note, search


def db():
    conn = sqlite3.connect(":memory:")
    create_schema(conn)
    return conn


def test_crud():
    conn = db()
    nid = add_note(conn, "Learn SQL", "joins")
    assert get_note(conn, nid) == {"id": nid, "title": "Learn SQL", "body": "joins"}
    assert get_note(conn, 999) is None


def test_search_case_insensitive():
    conn = db()
    add_note(conn, "Learn SQL")
    add_note(conn, "Buy milk")
    add_note(conn, "sql indexes")
    assert [n["title"] for n in search(conn, "SQL")] == ["Learn SQL", "sql indexes"]


def test_injection_is_harmless():
    conn = db()
    evil = "x'); DROP TABLE notes; --"
    nid = add_note(conn, evil)
    assert get_note(conn, nid)["title"] == evil
    assert search(conn, "' OR 1=1 --") == []


def test_committed():
    conn = db()
    add_note(conn, "kept")
    assert not conn.in_transaction, "commit after inserting"


def test_no_fstring_sql():
    src = inspect.getsource(solution)
    assert 'execute(f"' not in src and "execute(f'" not in src, "never build SQL with f-strings"
