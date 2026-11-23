# Given from earlier exercises. Do not change these.
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


class ChatState(TypedDict):
    messages: Annotated[list, add_messages]  # new messages are added to the list


# Your task:
def build_chat_graph(model):
    def call_model(state):
        reply = model.invoke(state["messages"])
        return {"messages": [reply]}

    graph = StateGraph(ChatState)
    graph.add_node("model", call_model)
    graph.add_edge(START, "model")
    graph.add_edge("model", END)
    return graph.compile()
