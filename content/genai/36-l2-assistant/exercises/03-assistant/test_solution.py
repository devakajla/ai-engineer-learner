import json
from types import SimpleNamespace as NS

import pytest

from solution import Ticket, assistant

REGISTRY = {
    "tutor": {"v1": "You are a {level} tutor."},
    "ticketer": {"v1": "Turn text into a ticket."},
}


class FakeClient:
    """Each item of `script` is a message (NS with content and tool_calls)."""

    def __init__(self, script):
        self.script = list(script)
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})
        message = self.script.pop(0) if len(self.script) > 1 else self.script[0]
        return NS(choices=[NS(message=message, finish_reason="stop")])


def text(content):
    return NS(role="assistant", content=content, tool_calls=None)


def tool_message(name, args, call_id="c1"):
    call = NS(id=call_id, type="function", function=NS(name=name, arguments=json.dumps(args)))
    return NS(role="assistant", content=None, tool_calls=[call])


def add(a, b):
    return a + b


TOOLS = [{"type": "function", "function": {"name": "add", "description": "Add", "parameters": {"type": "object", "properties": {}}}}]


def test_plain_text():
    client = FakeClient([text("A list holds items.")])
    out = assistant(client, REGISTRY, "tutor", {"level": "kind"}, "What is a list?")
    assert out == "A list holds items."
    call = client.calls[0]
    assert call["messages"][0] == {"role": "system", "content": "You are a kind tutor."}
    assert call["messages"][-1] == {"role": "user", "content": "What is a list?"}
    assert call["temperature"] == 0
    assert "tools" not in call, "no tools were given, so do not send any"


def test_examples_are_used():
    client = FakeClient([text("ok")])
    assistant(client, REGISTRY, "tutor", {"level": "x"}, "3+3?", examples=[("2+2", "4")])
    roles = [m["role"] for m in client.calls[0]["messages"]]
    assert roles == ["system", "user", "assistant", "user"]


def test_structured():
    client = FakeClient([text('{"title": "Login crash", "priority": 5}')])
    out = assistant(client, REGISTRY, "ticketer", {}, "Login crashes", model_class=Ticket)
    assert isinstance(out, Ticket) and out.priority == 5
    assert client.calls[0]["response_format"] == {"type": "json_object"}


def test_structured_repairs():
    client = FakeClient([text('{"title": "x", "priority": 9}'), text('{"title": "x", "priority": 2}')])
    out = assistant(client, REGISTRY, "ticketer", {}, "x", model_class=Ticket)
    assert out.priority == 2 and len(client.calls) == 2


def test_tools():
    client = FakeClient([tool_message("add", {"a": 2, "b": 3}), text("It is 5.")])
    out = assistant(client, REGISTRY, "tutor", {"level": "x"}, "2+3?", tools=TOOLS, functions={"add": add})
    assert out == "It is 5."
    assert len(client.calls) == 2
    last = client.calls[1]["messages"][-1]
    assert last["role"] == "tool" and last["content"] == "5"


def test_tools_without_functions_dict():
    client = FakeClient([tool_message("add", {"a": 1, "b": 1}), text("done")])
    out = assistant(client, REGISTRY, "tutor", {"level": "x"}, "q", tools=TOOLS)
    assert out == "done"
    assert client.calls[1]["messages"][-1]["content"].startswith("error: unknown tool")


def test_both_is_an_error_and_makes_no_call():
    client = FakeClient([text("x")])
    with pytest.raises(ValueError, match="not both"):
        assistant(client, REGISTRY, "tutor", {"level": "x"}, "q", tools=TOOLS, model_class=Ticket)
    assert client.calls == []
