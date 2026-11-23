# Given from earlier exercises. Do not change these.
from typing import Annotated, TypedDict

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


class ChatState(TypedDict):
    messages: Annotated[list, add_messages]


def build_graph(model):
    def call_model(state):
        return {"messages": [model.invoke(state["messages"])]}

    graph = StateGraph(ChatState)
    graph.add_node("model", call_model)
    graph.add_edge(START, "model")
    graph.add_edge("model", END)
    return graph


def build_memory_chat(model):
    return build_graph(model).compile(checkpointer=InMemorySaver())


# Your task:
def stream_nodes(app, state, config=None):
    names = []
    for update in app.stream(state, config, stream_mode="updates"):
        names.extend(update.keys())
    return names


def stream_reply(app, thread_id, text):
    config = {"configurable": {"thread_id": thread_id}}
    pieces = []
    for chunk, meta in app.stream({"messages": [HumanMessage(text)]}, config, stream_mode="messages"):
        if meta.get("langgraph_node") == "model":
            pieces.append(chunk.content)
    return "".join(pieces)
