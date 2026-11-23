from fastapi.testclient import TestClient

from solution import app

client = TestClient(app)


def test_defaults():
    assert client.get("/search?q=fastapi").json() == {"q": "fastapi", "limit": 10, "exact": False}


def test_all_params():
    assert client.get("/search?q=py&limit=5&exact=1").json() == {"q": "py", "limit": 5, "exact": True}


def test_validation():
    assert client.get("/search").status_code == 422
    assert client.get("/search?q=a").status_code == 422
    assert client.get("/search?q=" + "x" * 51).status_code == 422
    assert client.get("/search?q=abc&limit=100").status_code == 422
    assert client.get("/search?q=abc&limit=0").status_code == 422
