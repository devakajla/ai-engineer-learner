# Given from earlier exercises. Do not change these.
from typing import Annotated, TypedDict

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


class ChatState(TypedDict):
    messages: Annotated[list, add_messages]


def build_graph(model):
    def call_model(state):
        return {"messages": [model.invoke(state["messages"])]}

    graph = StateGraph(ChatState)
    graph.add_node("model", call_model)
    graph.add_edge(START, "model")
    graph.add_edge("model", END)
    return graph  # not compiled yet


def build_memory_chat(model):
    return build_graph(model).compile(checkpointer=InMemorySaver())


def chat(app, thread_id, text):
    config = {"configurable": {"thread_id": thread_id}}
    result = app.invoke({"messages": [HumanMessage(text)]}, config)
    return result["messages"][-1].content


# Your task:
def thread_messages(app, thread_id):
    config = {"configurable": {"thread_id": thread_id}}
    messages = app.get_state(config).values.get("messages", [])
    return [f"{m.type}: {m.content}" for m in messages]


def thread_count(app, thread_id):
    return len(thread_messages(app, thread_id))


def forget_thread(app, thread_id):
    app.checkpointer.delete_thread(thread_id)
