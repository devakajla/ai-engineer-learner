# Given from earlier exercises. Do not change these.
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class RouteState(TypedDict):
    question: str
    route: str
    answer: str


# Your task:
def classify(state):
    has_digit = any(ch.isdigit() for ch in state["question"])
    return {"route": "math" if has_digit else "chat"}


def math_node(state):
    return {"answer": "math handler: " + state["question"]}


def chat_node(state):
    return {"answer": "chat handler: " + state["question"]}


def pick_route(state):
    return state["route"]


def build_router_graph():
    graph = StateGraph(RouteState)
    graph.add_node("classify", classify)
    graph.add_node("math", math_node)
    graph.add_node("chat", chat_node)
    graph.add_edge(START, "classify")
    graph.add_conditional_edges("classify", pick_route, {"math": "math", "chat": "chat"})
    graph.add_edge("math", END)
    graph.add_edge("chat", END)
    return graph.compile()
