# Given from earlier exercises. Do not change these.
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class RouteState(TypedDict):
    question: str
    route: str
    answer: str


# Your task:
def classify(state):
    ...


def math_node(state):
    ...


def chat_node(state):
    ...


def pick_route(state):
    ...


def build_router_graph():
    ...
