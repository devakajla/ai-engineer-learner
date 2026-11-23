from fastapi.testclient import TestClient

from solution import app

client = TestClient(app)


def test_info_block():
    info = app.openapi()["info"]
    assert info["title"] == "Shop API"
    assert info["version"] == "2.1.0"
    assert info["description"] == "Small shop backend"


def test_tag_description():
    tags = app.openapi()["tags"]
    assert {"name": "items", "description": "Item operations"} in tags


def test_list_items_metadata():
    op = app.openapi()["paths"]["/items"]["get"]
    assert op["summary"] == "List items"
    assert op["operationId"] == "list_items"
    assert op["tags"] == ["items"]


def test_deprecated_route():
    op = app.openapi()["paths"]["/items/old"]["get"]
    assert op.get("deprecated") is True
    assert "deprecated" not in app.openapi()["paths"]["/items"]["get"]


def test_hidden_route_is_hidden_but_works():
    assert "/internal" not in app.openapi()["paths"], "include_in_schema=False hides it from the docs"
    r = client.get("/internal")
    assert r.status_code == 200 and r.json() == {"secret": True}


def test_routes_work():
    assert client.get("/items").json() == [{"id": 1}]
    assert client.get("/items/old").json() == [{"id": 1}]


def test_docs_url_moved():
    assert client.get("/documentation").status_code == 200
    assert client.get("/docs").status_code == 404
    assert client.get("/openapi.json").status_code == 200
