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
    ...


def stream_reply(app, thread_id, text):
    ...
