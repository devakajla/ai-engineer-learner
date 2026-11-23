from operator import add
from typing import Annotated, TypedDict

from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langgraph.graph import END, START, StateGraph

from solution import build_memory_chat, stream_nodes, stream_reply


class S(TypedDict):
    n: int
    log: Annotated[list, add]


def make_counter():
    graph = StateGraph(S)
    graph.add_node("one", lambda s: {"n": s["n"] + 1, "log": ["one"]})
    graph.add_node("two", lambda s: {"n": s["n"] * 2, "log": ["two"]})
    graph.add_edge(START, "one")
    graph.add_edge("one", "two")
    graph.add_edge("two", END)
    return graph.compile()


def test_stream_nodes_lists_the_nodes_in_order():
    assert stream_nodes(make_counter(), {"n": 1, "log": []}) == ["one", "two"]


def test_stream_nodes_with_a_config():
    app = build_memory_chat(FakeListChatModel(responses=["hi"]))
    from langchain_core.messages import HumanMessage

    config = {"configurable": {"thread_id": "t"}}
    assert stream_nodes(app, {"messages": [HumanMessage("yo")]}, config) == ["model"]


def test_stream_reply_collects_the_text_pieces():
    app = build_memory_chat(FakeListChatModel(responses=["Hello Dev"]))
    assert stream_reply(app, "t1", "hi") == "Hello Dev"


def test_stream_reply_arrives_in_more_than_one_piece():
    app = build_memory_chat(FakeListChatModel(responses=["abc"]))
    from langchain_core.messages import HumanMessage

    config = {"configurable": {"thread_id": "t"}}
    pieces = [c.content for c, m in app.stream({"messages": [HumanMessage("x")]}, config, stream_mode="messages")]
    assert len(pieces) > 1, "the fake model streams letter by letter, like a real model streams tokens"
