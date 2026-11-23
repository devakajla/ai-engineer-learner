import pytest
from fastapi.testclient import TestClient

from solution import app

client = TestClient(app)


def send(name="me.png", data=b"\x89PNG", content_type="image/png"):
    return client.post("/avatar", files={"file": (name, data, content_type)})


def test_valid_png():
    r = send()
    assert r.status_code == 201, r.text
    assert r.json() == {"filename": "me.png", "content_type": "image/png", "size": 4}


def test_valid_jpeg():
    r = send("a.jpg", b"x" * 10, "image/jpeg")
    assert r.status_code == 201 and r.json()["size"] == 10


@pytest.mark.parametrize("ctype", ["text/plain", "application/pdf", "image/gif"])
def test_wrong_type(ctype):
    r = send("x.bin", b"abc", ctype)
    assert r.status_code == 415, f"{ctype} should give 415"
    assert r.json() == {"detail": "Only PNG or JPEG images"}


def test_empty_file():
    r = send(data=b"")
    assert r.status_code == 400
    assert r.json() == {"detail": "Empty file"}


def test_size_limit_is_1024():
    assert send(data=b"x" * 1024).status_code == 201, "exactly 1024 bytes is allowed"
    r = send(data=b"x" * 1025)
    assert r.status_code == 413
    assert r.json() == {"detail": "File too large"}


def test_type_checked_before_size():
    assert send(data=b"x" * 5000, content_type="text/plain").status_code == 415


def test_only_base_name_is_returned():
    assert send(name="../../etc/passwd.png").json()["filename"] == "passwd.png"
    assert send(name="C:\\temp\\pic.png").json()["filename"] == "pic.png"


def test_missing_file_field():
    assert client.post("/avatar").status_code == 422
