"""Step 20 checks. Runs with the current directory = the learner's project folder."""

import json
from types import SimpleNamespace as NS

from copilot.agent import (
    AGENT_SYSTEM,
    agent_step,
    message_to_dict,
    run_agent_safe,
    tool_names_used,
)
from copilot.judge import parse_verdict

SPEC = {
    "paths": {
        "/tasks": {"get": {"summary": "List tasks"}, "post": {"summary": "Create a task"}},
        "/tasks/{id}": {"delete": {"summary": "Delete a task"}},
    }
}


def tool_call(id, name, arguments="{}"):
    return NS(id=id, function=NS(name=name, arguments=arguments))


def reply(content=None, calls=None):
    return NS(choices=[NS(message=NS(content=content, tool_calls=calls))])


class ScriptedClient:
    """Gives the prepared replies one after the other (the last one repeats). Records every call."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return self.replies[min(len(self.calls) - 1, len(self.replies) - 1)]


def test_earlier_steps_still_work():
    assert parse_verdict('{"score": 5}') == {"score": 5, "reason": ""}


def test_message_to_dict():
    plain = NS(content="hi", tool_calls=None)
    assert message_to_dict(plain) == {"role": "assistant", "content": "hi"}
    with_calls = NS(content=None, tool_calls=[tool_call("c1", "list_endpoints")])
    assert message_to_dict(with_calls) == {
        "role": "assistant",
        "content": None,
        "tool_calls": [{"id": "c1", "type": "function", "function": {"name": "list_endpoints", "arguments": "{}"}}],
    }


def test_agent_step_runs_the_tool_and_keeps_the_input_list():
    client = ScriptedClient([reply(calls=[tool_call("c1", "list_endpoints")])])
    messages = [{"role": "user", "content": "q"}]
    from copilot.spec_tools import FUNCTIONS, TOOLS

    out = agent_step(client, messages, TOOLS, FUNCTIONS, SPEC)
    assert out["done"] is False and out["answer"] is None
    assert len(messages) == 1, "the input list must not change"
    assert [m["role"] for m in out["messages"]] == ["user", "assistant", "tool"]
    assert out["messages"][-1]["tool_call_id"] == "c1"
    assert "GET /tasks" in out["messages"][-1]["content"]


def test_agent_step_without_tool_calls_is_done():
    client = ScriptedClient([reply("final")])
    from copilot.spec_tools import FUNCTIONS, TOOLS

    out = agent_step(client, [{"role": "user", "content": "q"}], TOOLS, FUNCTIONS, SPEC)
    assert out["done"] is True and out["answer"] == "final"


def test_agent_uses_a_tool_then_answers():
    client = ScriptedClient([
        reply(calls=[tool_call("c1", "list_endpoints")]),
        reply("There are 3 endpoints."),
    ])
    out = run_agent_safe(client, "How many endpoints?", SPEC)
    assert out["answer"] == "There are 3 endpoints."
    assert out["steps"] == 2 and out["stopped"] == "done"
    assert tool_names_used(out["messages"]) == ["list_endpoints"]
    assert client.calls[0]["messages"][0] == {"role": "system", "content": AGENT_SYSTEM}
    second = client.calls[1]["messages"]
    assert second[-1]["role"] == "tool" and "DELETE /tasks/{id}" in second[-1]["content"]


def test_bad_tool_arguments_go_back_to_the_model_as_text():
    client = ScriptedClient([
        reply(calls=[tool_call("c1", "describe_endpoint", json.dumps({"method": "GET", "path": "/nope"}))]),
        reply("No such endpoint."),
    ])
    out = run_agent_safe(client, "q", SPEC)
    tool_message = [m for m in out["messages"] if m["role"] == "tool"][0]
    assert tool_message["content"] == "error: no endpoint GET /nope"
    assert out["answer"] == "No such endpoint."


def test_step_cap():
    different = [reply(calls=[tool_call(f"c{i}", "describe_endpoint", json.dumps({"method": "GET", "path": f"/p{i}"}))])
                 for i in range(10)]
    out = run_agent_safe(ScriptedClient(different), "q", SPEC, max_steps=3)
    assert out["stopped"] == "max_steps" and out["steps"] == 3 and out["answer"] is None


def test_loop_guard_stops_the_same_call_again_and_again():
    same = reply(calls=[tool_call("c1", "list_endpoints")])
    client = ScriptedClient([same])
    out = run_agent_safe(client, "q", SPEC, max_steps=10, max_repeats=2)
    assert out["stopped"] == "loop" and out["steps"] == 3
    assert len(client.calls) == 3, "stop as soon as the call is repeated too often"
