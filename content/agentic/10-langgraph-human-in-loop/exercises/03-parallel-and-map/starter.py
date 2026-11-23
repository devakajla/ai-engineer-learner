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
    ...


def build_map_graph(work):
    ...
