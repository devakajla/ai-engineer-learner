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
    config = {"configurable": {"thread_id": thread_id}}
    history = list(app.get_state_history(config))
    history.reverse()  # the newest comes first, we want the oldest first
    return [{"step": s.metadata["step"], "next": list(s.next), "values": s.values} for s in history]


def find_checkpoint(app, thread_id, step):
    config = {"configurable": {"thread_id": thread_id}}
    for snapshot in app.get_state_history(config):
        if snapshot.metadata["step"] == step:
            return snapshot.config
    return None


def replay_from(app, thread_id, step):
    return app.invoke(None, find_checkpoint(app, thread_id, step))


def fork_from(app, thread_id, step, changes):
    old = find_checkpoint(app, thread_id, step)
    forked = app.update_state(old, changes)
    return app.invoke(None, forked)
