from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

from solution import convert_temp, run_langchain_agent

BOUND = []


class FakeToolModel(GenericFakeChatModel):
    """A fake chat model. bind_tools records the tools, like a real model would take them."""

    def bind_tools(self, tools, **kwargs):
        BOUND.append(tools)
        return self


def call(celsius, id="c1"):
    return AIMessage(content="", tool_calls=[{"name": "convert_temp", "args": {"celsius": celsius}, "id": id}])


def test_answers_without_tools():
    model = FakeToolModel(messages=iter([AIMessage(content="Hello!")]))
    assert run_langchain_agent(model, "hi", [convert_temp]) == "Hello!"


def test_tools_are_given_to_the_model():
    BOUND.clear()
    run_langchain_agent(FakeToolModel(messages=iter([AIMessage(content="ok")])), "hi", [convert_temp])
    assert BOUND == [[convert_temp]], "call model.bind_tools(tools) once"


def test_one_tool_round():
    model = FakeToolModel(messages=iter([call(100), AIMessage(content="It is 212 F.")]))
    assert run_langchain_agent(model, "100 C in F?", [convert_temp]) == "It is 212 F."


def test_two_tool_rounds():
    model = FakeToolModel(messages=iter([call(0, "a"), call(100, "b"), AIMessage(content="32 and 212")]))
    assert run_langchain_agent(model, "both", [convert_temp]) == "32 and 212"


def test_stops_after_max_steps():
    endless = iter(call(1, f"id{i}") for i in range(100))
    model = FakeToolModel(messages=endless)
    out = run_langchain_agent(model, "loop", [convert_temp], max_steps=3)
    assert out == "Stopped: too many steps."
    assert len(list(endless)) == 100 - 3, "exactly max_steps model calls"
