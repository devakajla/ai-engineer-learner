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

from solution import message_to_dict


def test_plain_message():
    msg = NS(content="Hello!", tool_calls=None)
    assert message_to_dict(msg) == {"role": "assistant", "content": "Hello!"}


def test_empty_list_means_no_key():
    msg = NS(content="Hi", tool_calls=[])
    assert "tool_calls" not in message_to_dict(msg)


def test_with_calls():
    msg = NS(content=None, tool_calls=[call("c1", "get_weather", '{"city": "Delhi"}'), call("c2", "add", '{"a": 1}')])
    out = message_to_dict(msg)
    assert out["role"] == "assistant" and out["content"] is None
    assert out["tool_calls"] == [
        {"id": "c1", "type": "function", "function": {"name": "get_weather", "arguments": '{"city": "Delhi"}'}},
        {"id": "c2", "type": "function", "function": {"name": "add", "arguments": '{"a": 1}'}},
    ]
