import base64
import json

from fastapi.testclient import TestClient

import solution
from solution import app

client = TestClient(app)


def setup_function():
    solution.EVENTS[:] = [{"id": i, "type": "click"} for i in range(1, 96)]


def walk(limit=20, insert_after_first=False):
    seen, cursor, pages = [], None, 0
    while True:
        url = f"/events?limit={limit}" + (f"&cursor={cursor}" if cursor else "")
        body = client.get(url).json()
        seen += [e["id"] for e in body["items"]]
        pages += 1
        if insert_after_first and pages == 1:
            solution.EVENTS.append({"id": 1000, "type": "new"})
        cursor = body["next_cursor"]
        if cursor is None:
            return seen, pages


def test_first_page():
    body = client.get("/events").json()
    assert [e["id"] for e in body["items"]] == list(range(95, 75, -1))
    assert json.loads(base64.urlsafe_b64decode(body["next_cursor"])) == {"id": 76}


def test_walk_all_once():
    seen, pages = walk()
    assert seen == list(range(95, 0, -1)) and pages == 5


def test_stable_with_inserts():
    seen, _ = walk(insert_after_first=True)
    assert seen == list(range(95, 0, -1)), "new events must not shift or duplicate pages"


def test_exact_multiple_has_no_empty_page():
    solution.EVENTS[:] = [{"id": i, "type": "x"} for i in range(1, 41)]
    seen, pages = walk(limit=20)
    assert len(seen) == 40 and pages == 2


def test_invalid_cursor():
    r = client.get("/events?cursor=not-a-cursor!!")
    assert r.status_code == 400 and r.json() == {"detail": "Invalid cursor"}
    assert client.get("/events?limit=51").status_code == 422
