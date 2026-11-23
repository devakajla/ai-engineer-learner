from fastapi.testclient import TestClient

import solution
from solution import app

client = TestClient(app)


def test_versioned_paths():
    assert client.get("/api/v1/users").json() == []
    assert client.get("/api/v1/users/7").json() == {"id": 7}
    assert client.get("/users").status_code == 404


def test_router_config():
    assert solution.router.prefix == "/users", "set prefix on the APIRouter"
    assert solution.router.tags == ["users"], "set tags on the APIRouter"


def test_tags_in_docs():
    paths = client.get("/openapi.json").json()["paths"]
    assert paths["/api/v1/users"]["get"]["tags"] == ["users"]
