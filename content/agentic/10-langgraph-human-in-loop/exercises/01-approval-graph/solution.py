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
    answer = interrupt({"question": f"Approve: {state['request']}?"})
    return {"approved": answer == "yes"}


def choose(state):
    return "run" if state["approved"] else "cancel"


def run_it(state):
    return {"result": "done: " + state["request"]}


def cancel_it(state):
    return {"result": "cancelled: " + state["request"]}


def build_approval_graph():
    graph = StateGraph(ApprovalState)
    graph.add_node("ask_human", ask_human)
    graph.add_node("run", run_it)
    graph.add_node("cancel", cancel_it)
    graph.add_edge(START, "ask_human")
    graph.add_conditional_edges("ask_human", choose, {"run": "run", "cancel": "cancel"})
    graph.add_edge("run", END)
    graph.add_edge("cancel", END)
    return graph.compile(checkpointer=InMemorySaver())


def start_request(app, thread_id, request):
    config = {"configurable": {"thread_id": thread_id}}
    result = app.invoke({"request": request, "approved": False, "result": ""}, config)
    return result["__interrupt__"][0].value["question"]


def answer_request(app, thread_id, answer):
    config = {"configurable": {"thread_id": thread_id}}
    return app.invoke(Command(resume=answer), config)
