from fastapi.testclient import TestClient

from solution import app

client = TestClient(app)


def ids(response):
    return [p["id"] for p in response.json()["items"]]


def test_default_sorted_by_name():
    r = client.get("/products")
    assert r.status_code == 200
    assert r.json()["total"] == 6
    assert ids(r) == [1, 4, 3, 2, 6, 5], "default sort is by name"


def test_category_is_case_insensitive():
    r = client.get("/products?category=Accessories")
    assert r.json()["total"] == 3
    assert ids(r) == [1, 2, 5]
    assert client.get("/products?category=toys").json() == {"total": 0, "items": []}


def test_price_range_and_sort():
    r = client.get("/products?min_price=50&max_price=200&sort=price")
    assert ids(r) == [5, 3]
    assert r.json()["total"] == 2
    assert ids(client.get("/products?sort=-price&limit=2")) == [4, 6]


def test_total_ignores_paging():
    r = client.get("/products?limit=2&offset=4")
    assert r.json()["total"] == 6, "total counts all matches, not only the page"
    assert ids(r) == [6, 5]
    assert ids(client.get("/products?offset=10")) == []


def test_invalid_range_is_400():
    r = client.get("/products?min_price=100&max_price=10")
    assert r.status_code == 400
    assert r.json() == {"detail": "min_price cannot be greater than max_price"}


def test_validation_errors():
    for query in ("limit=0", "limit=101", "offset=-1", "sort=bad", "min_price=-1", "limit=abc"):
        assert client.get(f"/products?{query}").status_code == 422, f"{query} should be 422"


def test_get_one_and_404():
    assert client.get("/products/3").json() == {"id": 3, "name": "Monitor", "category": "displays", "price": 199.0}
    r = client.get("/products/99")
    assert r.status_code == 404 and r.json() == {"detail": "Product not found"}
