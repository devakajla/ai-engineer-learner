# Given from earlier exercises. Do not change these.
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


# Given. State shape to copy (classes come in Python lesson 19).
class ReviewState(TypedDict):
    draft: str
    final: str


# Your task:
def apply_review(draft, review):
    ...


def review_node(state):
    ...


def build_review_graph():
    ...
