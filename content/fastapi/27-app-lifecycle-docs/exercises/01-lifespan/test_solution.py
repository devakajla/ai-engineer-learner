from fastapi.testclient import TestClient

from solution import EVENTS, app


def setup_function():
    EVENTS.clear()


def test_lifespan_runs_only_inside_with():
    client = TestClient(app)
    assert EVENTS == [], "creating TestClient does not start the lifespan"
    with client:
        assert EVENTS == ["start"]
    assert EVENTS == ["start", "stop"]


def test_visits_counter():
    with TestClient(app) as client:
        assert client.get("/visit").json() == {"visits": 1}
        assert client.get("/visit").json() == {"visits": 2}
        assert client.get("/visit").json() == {"visits": 3}


def test_counter_starts_again_on_new_start():
    with TestClient(app) as client:
        client.get("/visit")
        client.get("/visit")
    with TestClient(app) as client:
        assert client.get("/visit").json() == {"visits": 1}, "startup must set visits to 0 each time"


def test_events_route():
    with TestClient(app) as client:
        assert client.get("/events").json() == {"events": ["start"]}
    assert EVENTS == ["start", "stop"]

