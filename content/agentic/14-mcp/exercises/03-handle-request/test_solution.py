from solution import handle_request, make_notification, make_request


def add(a, b):
    return a + b


def boom(x):
    raise ValueError("bad input " + str(x))


TOOLS = {
    "add": {"description": "Add two numbers.", "params": {"a": "int", "b": "int"}, "func": add},
    "boom": {"description": "Always fails.", "params": {"x": "str"}, "func": boom},
}


def test_initialize_echoes_the_version_and_names_the_server():
    reply = handle_request(TOOLS, make_request(1, "initialize", {"protocolVersion": "2025-01-01"}))
    assert reply["id"] == 1
    assert reply["result"]["protocolVersion"] == "2025-01-01"
    assert reply["result"]["capabilities"] == {"tools": {}}
    assert reply["result"]["serverInfo"] == {"name": "demo", "version": "1.0"}


def test_tools_list():
    reply = handle_request(TOOLS, make_request(2, "tools/list"))
    tools = reply["result"]["tools"]
    assert [t["name"] for t in tools] == ["add", "boom"]
    assert tools[0] == {
        "name": "add",
        "description": "Add two numbers.",
        "inputSchema": {
            "type": "object",
            "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
            "required": ["a", "b"],
        },
    }


def test_tools_call_success():
    reply = handle_request(TOOLS, make_request(3, "tools/call", {"name": "add", "arguments": {"a": 2, "b": 3}}))
    assert reply == {"jsonrpc": "2.0", "id": 3, "result": {"content": [{"type": "text", "text": "5"}], "isError": False}}


def test_a_failing_tool_is_a_result_with_is_error_not_a_protocol_error():
    reply = handle_request(TOOLS, make_request(4, "tools/call", {"name": "boom", "arguments": {"x": "q"}}))
    assert "error" not in reply
    assert reply["result"] == {"content": [{"type": "text", "text": "Error: bad input q"}], "isError": True}


def test_unknown_tool_and_unknown_method_are_protocol_errors():
    reply = handle_request(TOOLS, make_request(5, "tools/call", {"name": "nope", "arguments": {}}))
    assert reply["error"] == {"code": -32602, "message": "Unknown tool: nope"}
    reply = handle_request(TOOLS, make_request(6, "resources/list"))
    assert reply["error"] == {"code": -32601, "message": "Method not found: resources/list"}
    assert reply["id"] == 6


def test_notifications_get_no_reply():
    assert handle_request(TOOLS, make_notification("notifications/initialized")) is None


def test_request_id_zero_still_gets_a_reply():
    assert handle_request(TOOLS, make_request(0, "tools/list"))["id"] == 0
