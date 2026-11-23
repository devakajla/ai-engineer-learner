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
    ...
