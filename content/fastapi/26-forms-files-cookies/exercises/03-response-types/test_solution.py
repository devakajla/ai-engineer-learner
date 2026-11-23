from fastapi.testclient import TestClient

from solution import app

client = TestClient(app)


def test_html_page():
    r = client.get("/page")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/html"), "use response_class=HTMLResponse"
    assert r.text == "<h1>Hello</h1>"


def test_redirect():
    r = client.get("/old", follow_redirects=False)
    assert r.status_code == 301
    assert r.headers["location"] == "/new"


def test_redirect_followed():
    r = client.get("/old")
    assert r.status_code == 200 and r.text == "new"


def test_plain_text():
    r = client.get("/new")
    assert r.headers["content-type"].startswith("text/plain")
    assert r.text == "new", "plain text must not have JSON quotes"


def test_download_file():
    r = client.get("/download")
    assert r.status_code == 200
    assert r.text == "line one\nline two\n"
    disposition = r.headers["content-disposition"]
    assert "attachment" in disposition and "report.txt" in disposition


def test_profile_leaves_out_none():
    r = client.get("/profile")
    assert r.status_code == 200
    assert r.json() == {"id": 1, "name": "Ana"}, "fields that are None must be left out"
