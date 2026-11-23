import inspect

import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations

import solution
from solution import downgrade, upgrade


def make():
    engine = sa.create_engine("sqlite://")
    with engine.begin() as conn:
        conn.execute(sa.text("CREATE TABLE users (id INTEGER PRIMARY KEY, full_name TEXT)"))
        conn.execute(sa.text("INSERT INTO users (full_name) VALUES ('Ada Lovelace'), ('Plato'), ('Guido van Rossum')"))
    return engine


def run(engine, fn):
    with engine.begin() as conn:
        fn(Operations(MigrationContext.configure(conn)))


def test_upgrade():
    engine = make()
    run(engine, upgrade)
    with engine.begin() as conn:
        rows = conn.execute(sa.text("SELECT first_name, last_name FROM users ORDER BY id")).all()
    assert [tuple(r) for r in rows] == [("Ada", "Lovelace"), ("Plato", ""), ("Guido", "van Rossum")]
    assert "full_name" not in {c["name"] for c in sa.inspect(engine).get_columns("users")}


def test_roundtrip():
    engine = make()
    run(engine, upgrade)
    run(engine, downgrade)
    with engine.begin() as conn:
        names = [r[0] for r in conn.execute(sa.text("SELECT full_name FROM users ORDER BY id"))]
    assert names == ["Ada Lovelace", "Plato", "Guido van Rossum"]
    assert {c["name"] for c in sa.inspect(engine).get_columns("users")} == {"id", "full_name"}


def test_parameterized_and_self_contained():
    src = inspect.getsource(solution)
    assert "from app" not in src, "don't import app models in migrations"
    assert ":id" in src, "use bound parameters in the UPDATE"
