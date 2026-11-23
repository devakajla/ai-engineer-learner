from solution import parse_request_line


def test_with_query():
    assert parse_request_line("GET /tasks?done=true&limit=5 HTTP/1.1") == {
        "method": "GET",
        "path": "/tasks",
        "query": {"done": "true", "limit": "5"},
        "version": "HTTP/1.1",
    }


def test_without_query():
    assert parse_request_line("DELETE /tasks/7 HTTP/1.1") == {
        "method": "DELETE",
        "path": "/tasks/7",
        "query": {},
        "version": "HTTP/1.1",
    }


def test_empty_value_and_root():
    r = parse_request_line("GET /?q= HTTP/2")
    assert r["path"] == "/" and r["query"] == {"q": ""} and r["version"] == "HTTP/2"
