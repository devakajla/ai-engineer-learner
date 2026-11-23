from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.messages import AIMessage, HumanMessage

from solution import build_chat_graph


def test_adds_the_model_reply_to_the_messages():
    app = build_chat_graph(FakeListChatModel(responses=["Hi there!"]))
    out = app.invoke({"messages": [HumanMessage("hello")]})
    assert [m.type for m in out["messages"]] == ["human", "ai"]
    assert out["messages"][-1].content == "Hi there!"


def test_model_sees_the_whole_history():
    seen = []

    class Spy(FakeListChatModel):
        def _generate(self, messages, *args, **kwargs):
            seen.append([m.content for m in messages])
            return super()._generate(messages, *args, **kwargs)

    app = build_chat_graph(Spy(responses=["ok"]))
    app.invoke({"messages": [HumanMessage("one"), AIMessage("two"), HumanMessage("three")]})
    assert seen == [["one", "two", "three"]]


def test_each_run_adds_exactly_one_message():
    app = build_chat_graph(FakeListChatModel(responses=["a", "b"]))
    first = app.invoke({"messages": [HumanMessage("1")]})
    second = app.invoke({"messages": first["messages"] + [HumanMessage("2")]})
    assert [m.content for m in second["messages"]] == ["1", "a", "2", "b"]
