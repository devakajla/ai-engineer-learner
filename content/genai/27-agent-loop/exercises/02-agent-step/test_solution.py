from types import SimpleNamespace as NS


def call(id, name, arguments):
    return NS(id=id, function=NS(name=name, arguments=arguments))


def reply(content=None, tool_calls=None):
    return NS(choices=[NS(message=NS(content=content, tool_calls=tool_calls))])


class FakeClient:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})
        return self.replies.pop(0)

from solution import agent_step

TOOLS = [{"type": "function", "function": {"name": "add"}}]


def add(a, b):
    return a + b


def test_done_when_no_calls():
    client = FakeClient([reply("It is 5.")])
    messages = [{"role": "user", "content": "q"}]
    out = agent_step(client, messages, TOOLS, {"add": add})
    assert out["done"] is True and out["answer"] == "It is 5."
    assert out["messages"] == messages + [{"role": "assistant", "content": "It is 5."}]
    assert client.calls[0]["tools"] == TOOLS


def test_runs_tools_in_order():
    client = FakeClient([reply(None, [call("c1", "add", '{"a": 1, "b": 2}'), call("c2", "add", '{"a": 5, "b": 5}')])])
    out = agent_step(client, [{"role": "user", "content": "q"}], TOOLS, {"add": add})
    assert out["done"] is False and out["answer"] is None
    roles = [m["role"] for m in out["messages"]]
    assert roles == ["user", "assistant", "tool", "tool"]
    assert out["messages"][2] == {"role": "tool", "tool_call_id": "c1", "content": "3"}
    assert out["messages"][3]["content"] == "10"


def test_tool_error_becomes_text():
    client = FakeClient([reply(None, [call("c1", "fly", "{}")])])
    out = agent_step(client, [], TOOLS, {"add": add})
    assert out["messages"][-1]["content"] == "error: unknown tool fly"


def test_input_list_unchanged():
    messages = [{"role": "user", "content": "q"}]
    agent_step(FakeClient([reply("ok")]), messages, TOOLS, {})
    assert messages == [{"role": "user", "content": "q"}]
