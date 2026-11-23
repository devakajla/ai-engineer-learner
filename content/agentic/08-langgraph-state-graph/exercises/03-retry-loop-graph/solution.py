# Given from earlier exercises. Do not change these.
from operator import add
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


class LoopState(TypedDict):
    tries: int
    ok: bool
    log: Annotated[list, add]


# Your task:
def build_retry_graph(try_once, max_tries):
    def attempt(state):
        tries = state["tries"] + 1
        ok = try_once(tries)
        return {"tries": tries, "ok": ok, "log": [f"try {tries}: {'ok' if ok else 'fail'}"]}

    def should_stop(state):
        if state["ok"] or state["tries"] >= max_tries:
            return "stop"
        return "again"

    graph = StateGraph(LoopState)
    graph.add_node("attempt", attempt)
    graph.add_edge(START, "attempt")
    graph.add_conditional_edges("attempt", should_stop, {"again": "attempt", "stop": END})
    return graph.compile()
