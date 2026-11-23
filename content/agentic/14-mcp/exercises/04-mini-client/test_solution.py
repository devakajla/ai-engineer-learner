import pytest

from solution import call_tool, connect, handle_request, make_error


def add(a, b):
    return a + b


def boom(x):
    raise ValueError("bad " + x)


TOOLS = {
    "add": {"description": "Add two numbers.", "params": {"a": "int", "b": "int"}, "func": add},
    "boom": {"description": "Fails.", "params": {"x": "str"}, "func": boom},
}


class Wire:
    """Plays the network: passes each message to the server and records it."""

    def __init__(self):
        self.sent = []

    def send(self, message):
        self.sent.append(message)
        return handle_request(TOOLS, message)


def test_connect_follows_the_handshake_and_returns_chat_tools():
    wire = Wire()
    tools = connect(wire.send)
    assert [(m.get("id"), m["method"]) for m in wire.sent] == [
        (1, "initialize"), (None, "notifications/initialized"), (2, "tools/list")]
    assert [t["function"]["name"] for t in tools] == ["add", "boom"]
    assert tools[0]["type"] == "function"
    assert tools[0]["function"]["parameters"]["required"] == ["a", "b"]


def test_call_tool_returns_the_text():
    wire = Wire()
    assert call_tool(wire.send, 7, "add", {"a": 2, "b": 5}) == "7"
    assert wire.sent[0] == {"jsonrpc": "2.0", "id": 7, "method": "tools/call",
                            "params": {"name": "add", "arguments": {"a": 2, "b": 5}}}


def test_a_failing_tool_gives_text_the_model_can_read():
    assert call_tool(Wire().send, 8, "boom", {"x": "q"}) == "Error: bad q"


def test_protocol_errors_raise():
    with pytest.raises(RuntimeError, match="Unknown tool: nope"):
        call_tool(Wire().send, 9, "nope", {})


def test_connect_raises_when_the_server_refuses():
    def refuse(message):
        return make_error(message["id"], -32000, "server busy") if "id" in message else None

    with pytest.raises(RuntimeError, match="server busy"):
        connect(refuse)
