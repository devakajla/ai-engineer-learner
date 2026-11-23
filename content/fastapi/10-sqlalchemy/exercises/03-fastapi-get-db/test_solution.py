import inspect

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import solution
from solution import Base, app, get_db

client = TestClient(app)


def test_crud():
    r = client.post("/notes", json={"text": "hello"})
    assert r.status_code == 201
    note = r.json()
    assert set(note) == {"id", "text", "created_at"} and note["created_at"]
    assert client.get(f"/notes/{note['id']}").json()["text"] == "hello"
    r404 = client.get("/notes/9999")
    assert r404.status_code == 404 and r404.json() == {"detail": "Note not found"}
    assert client.post("/notes", json={"text": ""}).status_code == 422


def test_list_newest_first():
    a = client.post("/notes", json={"text": "a"}).json()["id"]
    b = client.post("/notes", json={"text": "b"}).json()["id"]
    ids = [n["id"] for n in client.get("/notes").json()]
    assert ids.index(b) < ids.index(a)


def test_get_db_is_yield_dependency():
    assert inspect.isgeneratorfunction(get_db), "get_db must yield the session"


def test_override_db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, expire_on_commit=False)

    def override():
        with TestSession() as s:
            yield s

    app.dependency_overrides[get_db] = override
    try:
        assert client.get("/notes").json() == []
        client.post("/notes", json={"text": "isolated"})
        assert [n["text"] for n in client.get("/notes").json()] == ["isolated"]
    finally:
        app.dependency_overrides.clear()
