from fastapi.testclient import TestClient

import solution
from solution import app

client = TestClient(app)


def test_filters_hash():
    r = client.get("/users/1")
    assert r.status_code == 200
    assert r.json() == {"id": 1, "email": "dev@x.io", "name": "Dev"}


def test_store_not_mutated():
    client.get("/users/2")
    assert "password_hash" in solution.USERS[2], "don't delete the hash from storage; let response_model filter it"


def test_404():
    r = client.get("/users/99")
    assert r.status_code == 404
    assert r.json() == {"detail": "User not found"}


def test_openapi_documents_response():
    schema = client.get("/openapi.json").json()
    resp = schema["paths"]["/users/{user_id}"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
    assert resp.get("$ref", "").endswith("UserOut"), "use response_model=UserOut"
