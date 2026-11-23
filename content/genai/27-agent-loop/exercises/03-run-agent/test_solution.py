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

from solution import run_agent

TOOLS = [{"type": "function", "function": {"name": "add"}}]


def add(a, b):
    return a + b


def test_two_steps():
    client = FakeClient([reply(None, [call("c1", "add", '{"a": 1, "b": 2}')]), reply("The sum is 3.")])
    out = run_agent(client, "1 + 2?", TOOLS, {"add": add})
    assert out["answer"] == "The sum is 3." and out["steps"] == 2 and out["stopped"] == "done"
    assert [m["role"] for m in out["messages"]] == ["system", "user", "assistant", "tool", "assistant"]
    assert out["messages"][0]["content"] == "You are a helpful assistant."
    assert out["messages"][3]["content"] == "3"


def test_second_call_sees_tool_result():
    client = FakeClient([reply(None, [call("c1", "add", '{"a": 1, "b": 2}')]), reply("3")])
    run_agent(client, "q", TOOLS, {"add": add})
    assert [m["role"] for m in client.calls[1]["messages"]] == ["system", "user", "assistant", "tool"]


def test_answer_at_once():
    out = run_agent(FakeClient([reply("Hi")]), "hello", TOOLS, {}, system="Be brief.")
    assert out["steps"] == 1 and out["messages"][0] == {"role": "system", "content": "Be brief."}


def test_max_steps():
    replies = [reply(None, [call(f"c{i}", "add", '{"a": 1, "b": 1}')]) for i in range(10)]
    client = FakeClient(replies)
    out = run_agent(client, "q", TOOLS, {"add": add}, max_steps=3)
    assert out["answer"] is None and out["stopped"] == "max_steps" and out["steps"] == 3
    assert len(client.calls) == 3, "must stop calling the model after max_steps"
