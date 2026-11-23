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
    ...


def build_handoff_graph():
    ...
