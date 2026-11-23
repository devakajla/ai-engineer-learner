from types import SimpleNamespace as NS

from solution import chat_with_tools


def tool_call(name, arguments, call_id):
    return NS(id=call_id, type="function", function=NS(name=name, arguments=arguments))


def reply(content=None, tool_calls=None):
    return NS(choices=[NS(message=NS(role="assistant", content=content, tool_calls=tool_calls))])


class FakeClient:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})
        return self.replies.pop(0)


def add(a, b):
    return a + b


TOOLS = [{"type": "function", "function": {"name": "add"}}]
QUESTION = [{"role": "user", "content": "What is 2+3?"}]


def test_no_tool_needed():
    client = FakeClient([reply("Hello!")])
    assert chat_with_tools(client, QUESTION, TOOLS, {"add": add}) == "Hello!"
    assert len(client.calls) == 1
    assert client.calls[0]["tools"] == TOOLS


def test_empty_tool_calls_list_means_no_tool():
    client = FakeClient([reply("Hi", tool_calls=[])])
    assert chat_with_tools(client, QUESTION, TOOLS, {"add": add}) == "Hi"
    assert len(client.calls) == 1


def test_one_round():
    client = FakeClient([
        reply(tool_calls=[tool_call("add", '{"a": 2, "b": 3}', "c1")]),
        reply("It is 5."),
    ])
    assert chat_with_tools(client, QUESTION, TOOLS, {"add": add}) == "It is 5."
    assert len(client.calls) == 2
    second = client.calls[1]["messages"]
    assert second[0] == QUESTION[0]
    assert second[1]["role"] == "assistant", "after the question, send the assistant message with the tool calls"
    assert second[1]["tool_calls"] == [
        {"id": "c1", "type": "function", "function": {"name": "add", "arguments": '{"a": 2, "b": 3}'}}
    ]
    assert second[2] == {"role": "tool", "tool_call_id": "c1", "content": "5"}
    assert client.calls[1]["tools"] == TOOLS


def test_two_tool_calls_and_unknown_tool():
    client = FakeClient([
        reply(tool_calls=[tool_call("add", '{"a": 1, "b": 1}', "c1"), tool_call("fly", "{}", "c2")]),
        reply("done"),
    ])
    assert chat_with_tools(client, QUESTION, TOOLS, {"add": add}) == "done"
    tool_messages = [m for m in client.calls[1]["messages"] if m["role"] == "tool"]
    assert [m["tool_call_id"] for m in tool_messages] == ["c1", "c2"]
    assert tool_messages[1]["content"] == "error: unknown tool fly"


def test_input_messages_are_not_changed():
    client = FakeClient([reply(tool_calls=[tool_call("add", '{"a": 2, "b": 3}', "c1")]), reply("5")])
    messages = list(QUESTION)
    chat_with_tools(client, messages, TOOLS, {"add": add})
    assert messages == QUESTION, "do not change the list that was passed in"
