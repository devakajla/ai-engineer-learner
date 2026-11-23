"""The agent loop: the model picks tools, we run them, we repeat until it answers or a limit stops us."""

import json

from copilot.llm import DEFAULT_MODEL
from copilot.spec_tools import FUNCTIONS, TOOLS
from copilot.tools import run_tool_call

AGENT_SYSTEM = (
    "You are DevDocs Copilot. Use the tools to look inside the API spec. "
    "Answer only from what the tools return. If the tools do not show the answer, say you do not know."
)


def message_to_dict(message):
    """Turn the model's reply object into a plain dict we can send back in the next call."""
    result = {"role": "assistant", "content": message.content}
    if message.tool_calls:
        result["tool_calls"] = [
            {
                "id": call.id,
                "type": "function",
                "function": {"name": call.function.name, "arguments": call.function.arguments},
            }
            for call in message.tool_calls
        ]
    return result


def agent_step(client, messages, tools, functions, spec, model=DEFAULT_MODEL):
    """One turn: call the model once. If it asks for tools, run them all and add the results.

    Returns {"done", "answer", "messages"}. The input list is not changed.
    """
    response = client.chat.completions.create(model=model, messages=messages, tools=tools)
    message = response.choices[0].message
    new_messages = messages + [message_to_dict(message)]
    if not message.tool_calls:
        return {"done": True, "answer": message.content, "messages": new_messages}
    for call in message.tool_calls:
        new_messages = new_messages + [run_tool_call(call, functions, spec)]
    return {"done": False, "answer": None, "messages": new_messages}


def call_key(call):
    """A text that is the same for the same tool with the same arguments."""
    return call["function"]["name"] + "|" + call["function"]["arguments"]


def run_agent_safe(client, question, spec, tools=TOOLS, functions=FUNCTIONS, system=AGENT_SYSTEM,
                   max_steps=5, max_repeats=2, model=DEFAULT_MODEL):
    """Run the loop with two guards: a step cap and a repeated-call detector.

    Returns {"answer", "steps", "stopped", "messages"}. stopped is "done", "max_steps" or "loop".
    """
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": question},
    ]
    seen = {}
    for step in range(1, max_steps + 1):
        before = len(messages)
        result = agent_step(client, messages, tools, functions, spec, model=model)
        messages = result["messages"]
        if result["done"]:
            return {"answer": result["answer"], "steps": step, "stopped": "done", "messages": messages}
        for added in messages[before:]:
            for call in added.get("tool_calls", []):
                key = call_key(call)
                seen[key] = seen.get(key, 0) + 1
                if seen[key] > max_repeats:
                    return {"answer": None, "steps": step, "stopped": "loop", "messages": messages}
    return {"answer": None, "steps": max_steps, "stopped": "max_steps", "messages": messages}


def tool_names_used(messages):
    """The names of the tools the agent called, in order. Good for tests and for logs."""
    names = []
    for message in messages:
        for call in message.get("tool_calls", []):
            names.append(call["function"]["name"])
    return names


def load_spec(path):
    with open(path, encoding="utf-8") as file:
        return json.load(file)
