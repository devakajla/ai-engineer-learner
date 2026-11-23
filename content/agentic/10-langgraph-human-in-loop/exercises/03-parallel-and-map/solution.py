# Given. State shapes to copy (classes come in Python lesson 19).
from operator import add
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send


class ParallelState(TypedDict):
    text: str
    words: int
    chars: int
    report: str


class MapState(TypedDict):
    items: list
    results: Annotated[list, add]
    total: int


# Your task:
def build_parallel_graph():
    graph = StateGraph(ParallelState)
    graph.add_node("count_words", lambda s: {"words": len(s["text"].split())})
    graph.add_node("count_chars", lambda s: {"chars": len(s["text"])})
    graph.add_node("report", lambda s: {"report": f"{s['words']} words, {s['chars']} chars"})
    graph.add_edge(START, "count_words")
    graph.add_edge(START, "count_chars")
    graph.add_edge("count_words", "report")
    graph.add_edge("count_chars", "report")
    graph.add_edge("report", END)
    return graph.compile()


def build_map_graph(work):
    def fan_out(state):
        return [Send("worker", {"item": item}) for item in state["items"]]

    def worker(state):
        return {"results": [work(state["item"])]}

    def combine(state):
        return {"total": sum(state["results"])}

    graph = StateGraph(MapState)
    graph.add_node("worker", worker)
    graph.add_node("combine", combine)
    graph.add_conditional_edges(START, fan_out, ["worker"])
    graph.add_edge("worker", "combine")
    graph.add_edge("combine", END)
    return graph.compile()
