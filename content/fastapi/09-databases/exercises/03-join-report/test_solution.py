import sqlite3

from solution import add_index, busiest_users, open_tasks_per_user, setup


def make():
    conn = sqlite3.connect(":memory:")
    setup(conn)
    return conn


def test_open_tasks_per_user_includes_zero():
    assert open_tasks_per_user(make()) == [("ana@x.io", 2), ("dev@x.io", 1), ("zed@x.io", 0)]


def test_busiest():
    conn = make()
    assert busiest_users(conn, 2) == ["ana@x.io"]
    assert busiest_users(conn, 1) == ["ana@x.io", "dev@x.io"]
    assert busiest_users(conn, 5) == []


def test_index_used():
    conn = make()
    add_index(conn)
    names = [r[1] for r in conn.execute("PRAGMA index_list('tasks')").fetchall()]
    assert "ix_tasks_owner_done" in names
    plan = " ".join(str(r) for r in conn.execute("EXPLAIN QUERY PLAN SELECT * FROM tasks WHERE owner_id = 1 AND done = 0"))
    assert "ix_tasks_owner_done" in plan
