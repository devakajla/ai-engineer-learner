import inspect

import pytest
from fastapi.testclient import TestClient

import solution
from solution import DuplicateNoteError, InMemoryNoteRepository, NoteNotFoundError, NoteService, app

client = TestClient(app)


def test_service_without_http():
    svc = NoteService(InMemoryNoteRepository())
    note = svc.create("Buy milk")
    assert svc.get(note["id"]) == note
    with pytest.raises(DuplicateNoteError):
        svc.create("BUY MILK")
    with pytest.raises(NoteNotFoundError):
        svc.get(999)


def test_service_has_no_http():
    src = inspect.getsource(solution.NoteService)
    assert "HTTPException" not in src and "status." not in src, "services must not know about HTTP"


def test_routes():
    r = client.post("/notes", json={"title": "Read docs"})
    assert r.status_code == 201
    nid = r.json()["id"]
    assert client.get(f"/notes/{nid}").json() == {"id": nid, "title": "Read docs"}

    dup = client.post("/notes", json={"title": "read DOCS"})
    assert dup.status_code == 409 and dup.json() == {"detail": "Note already exists"}

    missing = client.get("/notes/999")
    assert missing.status_code == 404 and missing.json() == {"detail": "Note not found"}
