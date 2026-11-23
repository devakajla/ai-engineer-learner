# Given from earlier exercises. Do not change these.
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class PipeState(TypedDict):
    text: str
    log: list


# Your task:
def build_clean_subgraph():
    def strip_node(state):
        return {"text": state["text"].strip()}

    def lower_node(state):
        return {"text": state["text"].lower()}

    sub = StateGraph(PipeState)
    sub.add_node("strip", strip_node)
    sub.add_node("lower", lower_node)
    sub.add_edge(START, "strip")
    sub.add_edge("strip", "lower")
    sub.add_edge("lower", END)
    return sub.compile()


def build_pipeline():
    def tag(state):
        return {"log": state["log"] + ["cleaned"]}

    def finish(state):
        return {"text": state["text"] + "!", "log": state["log"] + ["finished"]}

    parent = StateGraph(PipeState)
    parent.add_node("clean", build_clean_subgraph())  # a compiled graph is a node
    parent.add_node("tag", tag)
    parent.add_node("finish", finish)
    parent.add_edge(START, "clean")
    parent.add_edge("clean", "tag")
    parent.add_edge("tag", "finish")
    parent.add_edge("finish", END)
    return parent.compile()
