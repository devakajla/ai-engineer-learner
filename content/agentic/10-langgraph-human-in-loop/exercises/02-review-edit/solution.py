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
    action = review.get("action")
    if action == "approve":
        return draft
    if action == "edit":
        return review.get("text", draft)
    return None


def review_node(state):
    review = interrupt({"draft": state["draft"], "options": ["approve", "edit", "reject"]})
    final = apply_review(state["draft"], review)
    return {"final": final if final is not None else "REJECTED"}


def build_review_graph():
    graph = StateGraph(ReviewState)
    graph.add_node("review", review_node)
    graph.add_edge(START, "review")
    graph.add_edge("review", END)
    return graph.compile(checkpointer=InMemorySaver())
