# Step 20 — An agent loop over the API spec

Until now Copilot followed a **fixed path**: search, build a prompt, answer. In this step the **model chooses**. It gets two tools that look inside an OpenAPI spec (from step 6) and may call them as often as it needs (lesson 27). You write the loop, and the two guards that keep it safe: a **step cap** and a **repeated-call detector**.

Your folder after this step (new files marked):

```
devdocs-copilot/
├── pyproject.toml
└── copilot/
    ├── agent.py        <- new
    ├── agent_cli.py    <- new
    └── ... (all files from step 19)
```

### 1. `copilot/agent.py`

```python
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
```

Read it in parts:

1. **`message_to_dict`**: the SDK gives you an object. The next call needs a plain dict. Without the `tool_calls` list in the assistant message, the following tool message has nothing to answer to, and the API refuses it.
2. **`agent_step`** is one turn. It makes **one** model call. No tool calls means the model is done. Otherwise it runs **every** requested tool (the model may ask for several at once) and appends one `tool` message for each. It builds a **new** list and never changes the one you pass in, so you can keep the old state for logs or retries.
3. **`run_tool_call`** (from step 6) never raises. A bad argument becomes `error: ...` text that goes back to the model, which can then try again. Your loop does not crash because the model made a typo.
4. **`run_agent_safe`** repeats `agent_step`. It has **two** guards, because a loop with no guard can run for ever and cost real money:
   - `max_steps` is a hard cap. When the loop reaches it, `stopped` is `"max_steps"` and there is no answer.
   - `call_key` joins the tool name and the argument text. If the **same** call happens more than `max_repeats` times, the agent is stuck, so the loop stops with `"loop"` early, before it burns all its steps.
5. **`stopped`** says **why** the run ended. A caller must be able to tell a real answer from a guard. Never return an empty string as if it were an answer.
6. **`tool_names_used`** reads the history and gives the tool names in order. It is the start of the "trajectory" check that you will use in step 23.

> An agent is a model in a `for` loop that you own. The model decides **what** to do. Your code decides **how long** it may go on.

### 2. Run it: `copilot/agent_cli.py`

```python
"""Ask the agent about an OpenAPI spec. Usage:

    python -m copilot.agent_cli openapi.json "which endpoints change a task?"
"""

import sys

from copilot.agent import load_spec, run_agent_safe, tool_names_used
from copilot.llm import get_client


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return
    spec = load_spec(sys.argv[1])
    result = run_agent_safe(get_client(), sys.argv[2], spec)
    print("tools used:", ", ".join(tool_names_used(result["messages"])) or "none")
    print(f"steps: {result['steps']}   stopped: {result['stopped']}")
    print(result["answer"] or "(no answer)")


if __name__ == "__main__":
    main()
```

With your TaskFlow spec (`curl http://localhost:8000/openapi.json > openapi.json`) try: `which endpoints change a task?` Look at **tools used** and **steps**. Then ask something the spec cannot answer, and check that the agent says it does not know instead of inventing an endpoint.

### Checkpoint

Run the tests of this step. Then run the CLI with your real key. Write down, for three questions, the tools used and the number of steps. If one run ends with `stopped: loop` or `max_steps`, read the messages to see what the model kept asking for. That is your first agent bug report.
