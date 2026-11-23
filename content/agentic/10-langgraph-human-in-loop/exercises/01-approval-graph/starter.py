# Given. State shape to copy (classes come in Python lesson 19).
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class ApprovalState(TypedDict):
    request: str
    approved: bool
    result: str


# Your task:
def ask_human(state):
    ...


def choose(state):
    ...


def run_it(state):
    ...


def cancel_it(state):
    ...


def build_approval_graph():
    ...


def start_request(app, thread_id, request):
    ...


def answer_request(app, thread_id, answer):
    ...
