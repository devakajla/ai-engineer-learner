# Given from earlier exercises. Do not change these.
from operator import add
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

def ask(client, prompt, system=None, temperature=0):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b", messages=messages, temperature=temperature
    )
    return response.choices[0].message.content.strip()


def run_worker(client, name, worker, task, context=""):
    prompt = task if not context else f"{task}\n\nWork so far:\n{context}"
    return {"worker": name, "output": ask(client, prompt, system=worker["system"])}


def format_results(results):
    return "\n".join(f"{r['worker']}: {r['output']}" for r in results)


def supervisor_prompt(task, workers, results):
    lines = "\n".join(f"- {name}: {w['description']}" for name, w in workers.items())
    done = format_results(results) if results else "(nothing yet)"
    return (
        f"Task: {task}\n\nWorkers:\n{lines}\n\nWork so far:\n{done}\n\n"
        "Which worker should act next? Reply with one worker name, or FINISH if the task is done."
    )


def parse_choice(reply, names):
    text = reply.strip().strip(".!\"' `")
    for name in names:
        if text.lower() == name.lower():
            return name
    if text.upper() == "FINISH":
        return "FINISH"
    return None


class SupState(TypedDict):
    task: str
    results: Annotated[list, add]
    next: str


class HandoffState(TypedDict):
    topic: str
    notes: str
    draft: str


# Your task:
def build_supervisor_graph(client, workers, max_steps=4):
    def supervisor(state):
        if len(state["results"]) >= max_steps:
            return {"next": "FINISH"}
        reply = ask(client, supervisor_prompt(state["task"], workers, state["results"]))
        return {"next": parse_choice(reply, list(workers)) or "FINISH"}

    def make_worker_node(name):
        def node(state):
            out = run_worker(client, name, workers[name], state["task"], format_results(state["results"]))
            return {"results": [out]}

        return node

    def route(state):
        return state["next"]

    graph = StateGraph(SupState)
    graph.add_node("supervisor", supervisor)
    for name in workers:
        graph.add_node(name, make_worker_node(name))
        graph.add_edge(name, "supervisor")
    graph.add_edge(START, "supervisor")
    paths = {name: name for name in workers}
    paths["FINISH"] = END
    graph.add_conditional_edges("supervisor", route, paths)
    return graph.compile()


def build_handoff_graph():
    def researcher(state):
        return Command(goto="writer", update={"notes": "facts about " + state["topic"]})

    def writer(state):
        return Command(goto=END, update={"draft": "Report: " + state["notes"]})

    graph = StateGraph(HandoffState)
    graph.add_node("researcher", researcher)
    graph.add_node("writer", writer)
    graph.add_edge(START, "researcher")
    return graph.compile()
