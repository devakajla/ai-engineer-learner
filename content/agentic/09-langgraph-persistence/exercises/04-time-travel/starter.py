# Given from earlier exercises. Do not change these.
from operator import add
from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class CounterState(TypedDict):
    n: int
    log: Annotated[list, add]


def build_counter():
    graph = StateGraph(CounterState)
    graph.add_node("inc", lambda s: {"n": s["n"] + 1, "log": ["inc"]})
    graph.add_node("double", lambda s: {"n": s["n"] * 2, "log": ["double"]})
    graph.add_edge(START, "inc")
    graph.add_edge("inc", "double")
    graph.add_edge("double", END)
    return graph.compile(checkpointer=InMemorySaver())


# Your task:
def list_checkpoints(app, thread_id):
    ...


def find_checkpoint(app, thread_id, step):
    ...


def replay_from(app, thread_id, step):
    ...


def fork_from(app, thread_id, step, changes):
    ...
