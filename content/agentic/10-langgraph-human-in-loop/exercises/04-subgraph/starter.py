# Given from earlier exercises. Do not change these.
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class PipeState(TypedDict):
    text: str
    log: list


# Your task:
def build_clean_subgraph():
    ...


def build_pipeline():
    ...
