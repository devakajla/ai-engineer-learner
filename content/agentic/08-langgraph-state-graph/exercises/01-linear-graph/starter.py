# Given. The state is a TypedDict: copy this shape (classes come in Python lesson 19).
from operator import add
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    text: str
    steps: Annotated[list, add]  # "add" means: new values are appended to the list


# Your task:
def clean(state):
    ...


def shout(state):
    ...


def build_linear_graph():
    ...
