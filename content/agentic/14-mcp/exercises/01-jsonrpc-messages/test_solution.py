from solution import classify, make_error, make_notification, make_request, make_result


def test_request_with_and_without_params():
    assert make_request(1, "tools/list") == {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
    assert make_request(2, "tools/call", {"name": "add"}) == {
        "jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "add"}}


def test_request_id_zero_is_kept():
    assert make_request(0, "ping")["id"] == 0


def test_notification_has_no_id():
    assert make_notification("notifications/initialized") == {"jsonrpc": "2.0", "method": "notifications/initialized"}
    assert "id" not in make_notification("x", {"a": 1})
    assert make_notification("x", {"a": 1})["params"] == {"a": 1}


def test_result_and_error():
    assert make_result(1, {"ok": True}) == {"jsonrpc": "2.0", "id": 1, "result": {"ok": True}}
    assert make_error(3, -32601, "Method not found") == {
        "jsonrpc": "2.0", "id": 3, "error": {"code": -32601, "message": "Method not found"}}


def test_classify_all_kinds():
    assert classify(make_request(1, "x")) == "request"
    assert classify(make_request(0, "x")) == "request", "id 0 is still an id"
    assert classify(make_notification("x")) == "notification"
    assert classify(make_result(1, {})) == "result"
    assert classify(make_error(1, -1, "bad")) == "error"
    assert classify({"hello": "world"}) == "invalid"
