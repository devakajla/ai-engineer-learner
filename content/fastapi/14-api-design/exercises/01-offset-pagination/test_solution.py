from fastapi.testclient import TestClient

from solution import PRODUCTS, app

client = TestClient(app)


def test_envelope_defaults():
    body = client.get("/products").json()
    assert set(body) == {"items", "total", "limit", "offset"}
    assert body["total"] == 57 and body["limit"] == 10 and len(body["items"]) == 10
    assert [p["id"] for p in body["items"]] == list(range(1, 11))


def test_paging_and_end():
    body = client.get("/products?limit=50&offset=50").json()
    assert [p["id"] for p in body["items"]] == list(range(51, 58))
    assert client.get("/products?offset=1000").json()["items"] == []


def test_filters():
    body = client.get("/products?category=books&limit=50").json()
    assert body["total"] == 19 and all(p["category"] == "books" for p in body["items"])
    assert client.get("/products?q=ITEM 0").json()["total"] == 9


def test_sorting_deterministic():
    items = client.get("/products?sort=-price&limit=50").json()["items"]
    expected = sorted(sorted(PRODUCTS, key=lambda p: p["id"]), key=lambda p: p["price"], reverse=True)[:50]
    assert [p["id"] for p in items] == [p["id"] for p in expected]
    assert client.get("/products?sort=name").json()["items"][0]["name"] == "Item 01"


def test_validation():
    for q in ("limit=0", "limit=51", "offset=-1", "sort=category", "sort=price;drop"):
        assert client.get(f"/products?{q}").status_code == 422
