"""Step 6 checks. Runs with the current directory = the learner's project folder."""

from types import SimpleNamespace as NS

from copilot.llm import chat_turn
from copilot.qa import answer_structured
from copilot.spec_tools import FUNCTIONS, TOOLS, ask_spec, describe_endpoint, list_endpoints
from copilot.tools import make_tool, run_tool_call

SPEC = {
    "paths": {
        "/tasks": {
            "get": {"summary": "List all tasks"},
            "post": {"summary": "Create a task"},
            "parameters": [],
        },
        "/tasks/{id}": {
            "get": {"summary": "Get one task", "parameters": [{"name": "id", "in": "path"}]},
            "delete": {"summary": "Delete a task"},
        },
    }
}


def tool_call(name, arguments, call_id="c1"):
    return NS(id=call_id, type="function", function=NS(name=name, arguments=arguments))


def reply(content=None, tool_calls=None):
    return NS(choices=[NS(message=NS(role="assistant", content=content, tool_calls=tool_calls), finish_reason="stop")])


class FakeClient:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})
        return self.replies.pop(0) if len(self.replies) > 1 else self.replies[0]


def test_earlier_steps_still_work():
    client = FakeClient([reply("Hi!")])
    assert chat_turn(client, [], "Hello")[0] == "Hi!"
    good = '{"answer": "a", "found": true, "confidence": "low", "quote": ""}'
    assert answer_structured(FakeClient([reply(good)]), "Q?", "D", base_delay=0).found is True


def test_make_tool():
    tool = make_tool("add", "Add.", {"a": ("number", "First")})
    assert tool == {
        "type": "function",
        "function": {
            "name": "add",
            "description": "Add.",
            "parameters": {
                "type": "object",
                "properties": {"a": {"type": "number", "description": "First"}},
                "required": ["a"],
            },
        },
    }


def test_list_endpoints():
    assert list_endpoints(SPEC) == ["GET /tasks", "POST /tasks", "GET /tasks/{id}", "DELETE /tasks/{id}"]
    assert list_endpoints({}) == []


def test_describe_endpoint():
    text = describe_endpoint(SPEC, "get", "/tasks/{id}")
    assert "GET /tasks/{id}" in text and "Get one task" in text and "id (path)" in text
    assert describe_endpoint(SPEC, "post", "/nope").startswith("error: no endpoint POST /nope")
    assert describe_endpoint(SPEC, "PATCH", "/tasks").startswith("error:")


def test_tools_and_functions_match():
    names = [tool["function"]["name"] for tool in TOOLS]
    assert names == ["list_endpoints", "describe_endpoint"]
    assert set(FUNCTIONS) == set(names), "every tool needs a function with the same name"
    assert TOOLS[1]["function"]["parameters"]["required"] == ["method", "path"]


def test_run_tool_call_passes_the_spec():
    message = run_tool_call(tool_call("list_endpoints", "{}"), FUNCTIONS, SPEC)
    assert message["role"] == "tool" and message["tool_call_id"] == "c1"
    assert "GET /tasks" in message["content"] and "DELETE /tasks/{id}" in message["content"]
    args = '{"method": "get", "path": "/tasks"}'
    assert "List all tasks" in run_tool_call(tool_call("describe_endpoint", args), FUNCTIONS, SPEC)["content"]


def test_run_tool_call_errors_become_text():
    assert run_tool_call(tool_call("fly", "{}"), FUNCTIONS, SPEC)["content"] == "error: unknown tool fly"
    assert run_tool_call(tool_call("list_endpoints", "oops"), FUNCTIONS, SPEC)["content"] == "error: invalid arguments"
    bad = run_tool_call(tool_call("describe_endpoint", '{"method": "get"}'), FUNCTIONS, SPEC)["content"]
    assert bad.startswith("error: "), "a missing argument must not crash"


def test_ask_spec_full_round():
    client = FakeClient([
        reply(tool_calls=[tool_call("list_endpoints", "{}")]),
        reply("You can list tasks with GET /tasks."),
    ])
    answer = ask_spec(client, SPEC, "What can I do with tasks?")
    assert answer == "You can list tasks with GET /tasks."
    assert len(client.calls) == 2
    assert client.calls[0]["tools"] == TOOLS, "send the tools"
    second = client.calls[1]["messages"]
    assert second[-2]["role"] == "assistant" and second[-2]["tool_calls"][0]["function"]["name"] == "list_endpoints"
    assert second[-1]["role"] == "tool" and "GET /tasks" in second[-1]["content"], "the tool result goes back to the model"


def test_ask_spec_without_tools():
    client = FakeClient([reply("No tool needed.")])
    assert ask_spec(client, SPEC, "Hello") == "No tool needed."
    assert len(client.calls) == 1
