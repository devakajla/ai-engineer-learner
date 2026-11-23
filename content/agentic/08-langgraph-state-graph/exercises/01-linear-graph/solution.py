# Given. The state is a TypedDict: copy this shape (classes come in Python lesson 19).
from operator import add
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    text: str
    steps: Annotated[list, add]  # "add" means: new values are appended to the list


# Your task:
def clean(state):
    return {"text": state["text"].strip(), "steps": ["clean"]}


def shout(state):
    return {"text": state["text"].upper() + "!", "steps": ["shout"]}


def build_linear_graph():
    graph = StateGraph(State)
    graph.add_node("clean", clean)
    graph.add_node("shout", shout)
    graph.add_edge(START, "clean")
    graph.add_edge("clean", "shout")
    graph.add_edge("shout", END)
    return graph.compile()
