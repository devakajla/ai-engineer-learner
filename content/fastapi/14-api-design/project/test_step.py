"""Step 14 checks. Runs with the current directory = the learner's project folder."""

import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool


@pytest.fixture(scope="module")
def client(tmp_path_factory):
    import app.db.models  # noqa: F401
    from app.db.base import Base
    from app.db.session import get_db
    from app.main import create_app

    path = tmp_path_factory.mktemp("db") / "t.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{path}", poolclass=NullPool)

    async def create():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(create())
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async def override():
        async with Session() as s:
            yield s

    app = create_app()
    app.dependency_overrides[get_db] = override
    c = TestClient(app)
    for i in range(25):
        title = f"{'Report' if i % 5 == 0 else 'Task'} {i:02d}"
        c.post("/api/v1/tasks", json={"title": title, "priority": "high" if i % 2 else "low",
                                      "due_date": f"2026-12-{(i % 9) + 1:02d}T00:00:00Z"})
    for i in range(0, 25, 3):
        c.patch(f"/api/v1/tasks/{i + 1}", json={"done": True})
    return c


def ids(body):
    return [t["id"] for t in body["items"]]


def test_envelope(client):
    body = client.get("/api/v1/tasks").json()
    assert set(body) == {"items", "total", "limit", "offset"}
    assert body["total"] == 25 and body["limit"] == 20 and body["offset"] == 0
    assert ids(body) == list(range(25, 5, -1)), "default sort is -id (newest first)"


def test_paging_covers_everything_once(client):
    seen = []
    for offset in range(0, 25, 7):
        seen += ids(client.get(f"/api/v1/tasks?limit=7&offset={offset}&sort=id").json())
    assert seen == list(range(1, 26))
    assert client.get("/api/v1/tasks?offset=100").json()["items"] == []


def test_filters_and_total(client):
    done = client.get("/api/v1/tasks?done=true&limit=100").json()
    assert done["total"] == 9 and all(t["done"] for t in done["items"])
    high = client.get("/api/v1/tasks?priority=high&done=false&limit=100").json()
    assert all(t["priority"] == "high" and not t["done"] for t in high["items"])
    assert high["total"] == len(high["items"])


def test_search(client):
    body = client.get("/api/v1/tasks?q=report&limit=100").json()
    assert body["total"] == 5 and all("Report" in t["title"] for t in body["items"])


def test_sorting(client):
    titles = [t["title"] for t in client.get("/api/v1/tasks?sort=title&limit=100").json()["items"]]
    assert titles == sorted(titles)
    due = client.get("/api/v1/tasks?sort=-due_date&limit=100").json()["items"]
    pairs = [(t["due_date"], t["id"]) for t in due]
    assert pairs == sorted(pairs, key=lambda p: (p[0], p[1]), reverse=True), "use id as a tie-breaker"


def test_validation(client):
    for q in ("sort=priority", "sort=id;drop", "limit=0", "limit=101", "offset=-1", "q="):
        assert client.get(f"/api/v1/tasks?{q}").status_code == 422, q
