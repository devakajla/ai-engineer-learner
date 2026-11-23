import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations

from solution import downgrade, upgrade


def run(engine, fn):
    with engine.begin() as conn:
        fn(Operations(MigrationContext.configure(conn)))


def test_upgrade_creates_table():
    engine = sa.create_engine("sqlite://")
    run(engine, upgrade)
    insp = sa.inspect(engine)
    cols = {c["name"]: c for c in insp.get_columns("projects")}
    assert set(cols) == {"id", "name", "archived", "created_at"}
    assert cols["name"]["nullable"] is False
    assert "ix_projects_archived" in [i["name"] for i in insp.get_indexes("projects")]
    with engine.begin() as conn:
        conn.execute(sa.text("INSERT INTO projects (name) VALUES ('TaskFlow')"))
        row = conn.execute(sa.text("SELECT archived, created_at FROM projects")).one()
        assert row.archived in (0, False) and row.created_at is not None, "use server defaults"
        with pytest.raises(sa.exc.IntegrityError):
            conn.execute(sa.text("INSERT INTO projects (name) VALUES ('TaskFlow')"))


def test_downgrade_removes_everything():
    engine = sa.create_engine("sqlite://")
    run(engine, upgrade)
    run(engine, downgrade)
    assert "projects" not in sa.inspect(engine).get_table_names()
