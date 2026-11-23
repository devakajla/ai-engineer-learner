import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations

from solution import downgrade, upgrade


def make():
    engine = sa.create_engine("sqlite://")
    with engine.begin() as conn:
        conn.execute(sa.text("CREATE TABLE tasks (id INTEGER PRIMARY KEY, title TEXT NOT NULL)"))
        conn.execute(sa.text("INSERT INTO tasks (title) VALUES ('a'), ('b')"))
    return engine


def run(engine, fn):
    with engine.begin() as conn:
        fn(Operations(MigrationContext.configure(conn)))


def test_upgrade_backfills_existing_rows():
    engine = make()
    run(engine, upgrade)
    with engine.begin() as conn:
        assert [r[0] for r in conn.execute(sa.text("SELECT status FROM tasks ORDER BY id"))] == ["todo", "todo"]
    cols = {c["name"]: c for c in sa.inspect(engine).get_columns("tasks")}
    assert cols["status"]["nullable"] is False
    assert "ix_tasks_status" in [i["name"] for i in sa.inspect(engine).get_indexes("tasks")]


def test_downgrade_keeps_data():
    engine = make()
    run(engine, upgrade)
    run(engine, downgrade)
    assert {c["name"] for c in sa.inspect(engine).get_columns("tasks")} == {"id", "title"}
    with engine.begin() as conn:
        assert conn.execute(sa.text("SELECT COUNT(*) FROM tasks")).scalar() == 2
