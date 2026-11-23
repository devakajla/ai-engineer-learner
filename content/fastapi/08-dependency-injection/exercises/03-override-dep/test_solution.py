from fastapi.testclient import TestClient

from solution import EmailNotifier, app, get_notifier

client = TestClient(app)


class FakeNotifier:
    def __init__(self):
        self.calls = []

    def send(self, to, message):
        self.calls.append((to, message))


def test_real_notifier_shared():
    assert get_notifier() is get_notifier(), "return one shared instance"
    r = client.post("/comments", json={"author": "dev@x.io", "text": "hi"})
    assert r.status_code == 201
    assert ("dev@x.io", "Thanks for your comment") in get_notifier().sent


def test_override_with_fake():
    fake = FakeNotifier()
    app.dependency_overrides[get_notifier] = lambda: fake
    try:
        r = client.post("/comments", json={"author": "ana@x.io", "text": "nice"})
        assert r.json()["author"] == "ana@x.io" and isinstance(r.json()["id"], int)
        assert fake.calls == [("ana@x.io", "Thanks for your comment")]
    finally:
        app.dependency_overrides.clear()


def test_email_notifier_class():
    n = EmailNotifier()
    n.send("a", "b")
    assert n.sent == [("a", "b")]
