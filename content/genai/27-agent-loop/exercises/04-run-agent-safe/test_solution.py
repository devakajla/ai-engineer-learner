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

from solution import run_agent_safe

TOOLS = [{"type": "function", "function": {"name": "add"}}]


def add(a, b):
    return a + b


def same(i):
    return reply(None, [call(f"c{i}", "add", '{"a": 1, "b": 1}')])


def test_loop_stops_on_third_repeat():
    client = FakeClient([same(i) for i in range(10)])
    out = run_agent_safe(client, "q", TOOLS, {"add": add})
    assert out["stopped"] == "loop" and out["steps"] == 3 and out["answer"] is None
    assert len(client.calls) == 3
    assert out["messages"][-1]["role"] == "tool"


def test_max_repeats_setting():
    client = FakeClient([same(i) for i in range(10)])
    out = run_agent_safe(client, "q", TOOLS, {"add": add}, max_repeats=1)
    assert out["steps"] == 2


def test_different_arguments_are_fine():
    replies = [reply(None, [call(f"c{i}", "add", '{"a": %d, "b": 1}' % i)]) for i in range(4)] + [reply("done")]
    out = run_agent_safe(FakeClient(replies), "q", TOOLS, {"add": add}, max_steps=6)
    assert out["stopped"] == "done" and out["steps"] == 5


def test_max_steps_still_works():
    replies = [reply(None, [call(f"c{i}", "add", '{"a": %d, "b": 1}' % i)]) for i in range(10)]
    out = run_agent_safe(FakeClient(replies), "q", TOOLS, {"add": add}, max_steps=3)
    assert out["stopped"] == "max_steps" and out["steps"] == 3


def test_repeats_counted_across_steps_with_other_calls_between():
    replies = [same(0), reply(None, [call("x", "add", '{"a": 9, "b": 9}')]), same(1), same(2), reply("done")]
    out = run_agent_safe(FakeClient(replies), "q", TOOLS, {"add": add}, max_steps=6)
    assert out["stopped"] == "loop" and out["steps"] == 4


def test_plain_answer():
    out = run_agent_safe(FakeClient([reply("Hi")]), "hello", TOOLS, {})
    assert out == {"answer": "Hi", "steps": 1, "stopped": "done", "messages": out["messages"]}
