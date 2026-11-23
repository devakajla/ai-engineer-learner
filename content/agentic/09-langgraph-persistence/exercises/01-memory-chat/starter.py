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
    return graph  # not compiled yet


# Your task:
def build_memory_chat(model):
    ...


def chat(app, thread_id, text):
    ...
