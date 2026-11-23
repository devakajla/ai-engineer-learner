from fastapi.testclient import TestClient
from sqlalchemy import event

from solution import app, engine

client = TestClient(app)


def expected():
    out = []
    for u in range(1, 31):
        n = u % 4
        out.append({
            "id": u,
            "email": f"user{u}@x.io",
            "open_tasks": sum(1 for t in range(n) if t % 2 != 0),
            "latest_task": f"u{u}-t{n - 1}" if n else None,
        })
    return out


def test_same_response():
    assert client.get("/users").json() == expected()


def test_query_budget():
    statements = []

    def count(*args):
        statements.append(args[2])

    event.listen(engine, "before_cursor_execute", count)
    try:
        client.get("/users")
    finally:
        event.remove(engine, "before_cursor_execute", count)
    assert len(statements) <= 2, f"{len(statements)} queries — still N+1"
