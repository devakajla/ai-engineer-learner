from types import SimpleNamespace as NS


class FakeClient:
    """Returns the replies one by one (the last one repeats). Records every call."""

    def __init__(self, *replies):
        self.replies = list(replies)
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})
        index = min(len(self.calls) - 1, len(self.replies) - 1)
        return NS(choices=[NS(message=NS(content=self.replies[index]))])


from solution import react_agent


def add(a, b):
    return a + b


def div(a, b):
    return a / b


FUNCS = {"add": add, "div": div}
CALL = 'Thought: use add\nAction: add\nAction Input: {"a": 2, "b": 3}'


def test_action_then_final():
    client = FakeClient(CALL, "Thought: done\nFinal Answer: 5")
    out = react_agent(client, "What is 2 + 3?", FUNCS)
    assert out == {"answer": "5", "stopped": "final", "steps": 2}
    second = client.calls[1]["messages"]
    assert second[-1] == {"role": "user", "content": "Observation: 5"}
    assert second[-2] == {"role": "assistant", "content": CALL}


def test_first_messages():
    client = FakeClient("Final Answer: hi")
    react_agent(client, "Say hi", FUNCS)
    msgs = client.calls[0]["messages"]
    assert [m["role"] for m in msgs] == ["system", "user"]
    assert msgs[1]["content"] == "Say hi"
    for name in FUNCS:
        assert name in msgs[0]["content"], f"the system message must list the tool {name}"
    assert client.calls[0]["temperature"] == 0


def test_final_at_once():
    client = FakeClient("Thought: easy\nFinal Answer: 42")
    assert react_agent(client, "q", FUNCS) == {"answer": "42", "stopped": "final", "steps": 1}


def test_unknown_tool():
    client = FakeClient('Action: fly\nAction Input: {}', "Final Answer: sorry")
    out = react_agent(client, "q", FUNCS)
    assert out["steps"] == 2
    assert client.calls[1]["messages"][-1]["content"] == "Observation: error: unknown tool fly"


def test_tool_exception_becomes_observation():
    client = FakeClient('Action: div\nAction Input: {"a": 1, "b": 0}', "Final Answer: cannot")
    react_agent(client, "q", FUNCS)
    assert client.calls[1]["messages"][-1]["content"] == "Observation: error: ZeroDivisionError: division by zero"


def test_parse_errors_become_observations():
    client = FakeClient("I will think.", 'Action: add\nAction Input: {bad', "Final Answer: ok")
    out = react_agent(client, "q", FUNCS)
    assert out == {"answer": "ok", "stopped": "final", "steps": 3}
    assert client.calls[1]["messages"][-1]["content"] == "Observation: error: no action"
    assert client.calls[2]["messages"][-1]["content"] == "Observation: error: bad arguments"


def test_max_steps():
    client = FakeClient(CALL)
    out = react_agent(client, "q", FUNCS, max_steps=3)
    assert out == {"answer": None, "stopped": "max_steps", "steps": 3}
    assert len(client.calls) == 3


def test_wrong_argument_names_become_an_error_text():
    client = FakeClient('Action: add\nAction Input: {"x": 1}', "Final Answer: x")
    react_agent(client, "q", FUNCS)
    obs = client.calls[1]["messages"][-1]["content"]
    assert obs.startswith("Observation: error: TypeError")


def test_final_answer_keeps_following_lines():
    client = FakeClient("Final Answer: line one\nline two")
    assert react_agent(client, "q", FUNCS)["answer"] == "line one\nline two"
