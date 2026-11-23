# Step 6 — Tools: let Copilot look inside an API spec

So far you pasted the document into the prompt. That works for a small text. A real API spec is big, and the model should **look things up**, not read everything.

In this step you give Copilot two **tools**:

- `list_endpoints`: what endpoints exist?
- `describe_endpoint`: what does this one do, and what parameters does it take?

The model decides when to use them. Your code runs them. (Lesson 11.)

Our "spec" is an **OpenAPI** document, loaded into a Python dictionary. It is the standard way to describe an API. Its important part is `paths`:

```python
spec = {
    "paths": {
        "/tasks": {
            "get": {"summary": "List all tasks"},
            "post": {"summary": "Create a task"},
        },
        "/tasks/{id}": {
            "get": {"summary": "Get one task", "parameters": [{"name": "id", "in": "path"}]},
        },
    }
}
```

### 1. The tool machinery: `copilot/tools.py`

Three functions from the lesson, with one change: every tool function gets the `spec` as its **first argument**. That way your tools read the spec you pass in, with no hidden global data.

```python
import json

from copilot.llm import DEFAULT_MODEL


def make_tool(name, description, params):
    """Describe one tool to the model. params is {name: (json type, description)}."""
    properties = {}
    for param, (kind, text) in params.items():
        properties[param] = {"type": kind, "description": text}
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {"type": "object", "properties": properties, "required": list(params)},
        },
    }


def run_tool_call(call, functions, spec):
    """Run the function the model asked for. Never raise: errors go back to the model as text."""
    name = call.function.name
    if name not in functions:
        content = f"error: unknown tool {name}"
    else:
        try:
            args = json.loads(call.function.arguments)
        except json.JSONDecodeError:
            args = None
        if not isinstance(args, dict):
            content = "error: invalid arguments"
        else:
            try:
                content = str(functions[name](spec, **args))
            except Exception as error:
                content = f"error: {error}"
    return {"role": "tool", "tool_call_id": call.id, "content": content}


def chat_with_tools(client, messages, tools, functions, spec, model=DEFAULT_MODEL):
    """One round of tool calling. Returns the final text."""
    response = client.chat.completions.create(model=model, messages=messages, tools=tools)
    message = response.choices[0].message
    if not message.tool_calls:
        return message.content
    assistant_message = {
        "role": "assistant",
        "content": message.content,
        "tool_calls": [
            {
                "id": call.id,
                "type": "function",
                "function": {"name": call.function.name, "arguments": call.function.arguments},
            }
            for call in message.tool_calls
        ],
    }
    tool_messages = [run_tool_call(call, functions, spec) for call in message.tool_calls]
    next_messages = messages + [assistant_message] + tool_messages
    response = client.chat.completions.create(model=model, messages=next_messages, tools=tools)
    return response.choices[0].message.content
```

> **Why `except Exception` here, when we said to catch specific errors?** This is a boundary: the model chooses what to call, so anything can go wrong. The error text goes **back to the model**, which can then fix its call. That is the one place where a broad catch is right.

### 2. The tools themselves: `copilot/spec_tools.py`

```python
"""Tools that let the model look inside an OpenAPI spec (a dictionary)."""

from copilot.llm import build_messages
from copilot.tools import chat_with_tools, make_tool

HTTP_METHODS = ("get", "post", "put", "patch", "delete")


def list_endpoints(spec):
    """Every endpoint as 'METHOD /path'."""
    found = []
    for path, item in spec.get("paths", {}).items():
        for method in HTTP_METHODS:
            if method in item:
                found.append(f"{method.upper()} {path}")
    return found


def describe_endpoint(spec, method, path):
    """A short text about one endpoint, or an error text the model can read."""
    item = spec.get("paths", {}).get(path, {})
    operation = item.get(method.lower())
    if operation is None:
        return f"error: no endpoint {method.upper()} {path}"
    lines = [f"{method.upper()} {path}", f"Summary: {operation.get('summary', '(none)')}"]
    names = [f"{p['name']} ({p.get('in', 'query')})" for p in operation.get("parameters", [])]
    if names:
        lines.append("Parameters: " + ", ".join(names))
    return "\n".join(lines)
```

The first two are plain, testable Python. They know nothing about the model. Keep it that way: **logic first, model last**.

Now the wiring. The model's tool functions receive `(spec, **args)`:

```python
def _list_endpoints_tool(spec):
    return "\n".join(list_endpoints(spec))


def _describe_endpoint_tool(spec, method, path):
    return describe_endpoint(spec, method, path)


TOOLS = [
    make_tool("list_endpoints", "List every endpoint of the API, as 'METHOD /path'.", {}),
    make_tool(
        "describe_endpoint",
        "Describe one endpoint: its summary and parameters.",
        {"method": ("string", "HTTP method, like GET"), "path": ("string", "Path, like /tasks")},
    ),
]

FUNCTIONS = {
    "list_endpoints": _list_endpoints_tool,
    "describe_endpoint": _describe_endpoint_tool,
}


def ask_spec(client, spec, question):
    """Answer a question about the API by letting the model call the tools."""
    messages = build_messages([], question)
    return chat_with_tools(client, messages, TOOLS, FUNCTIONS, spec)
```

### 3. Try it for real

Use any small OpenAPI JSON file. A FastAPI app gives you one for free: run your TaskFlow API and open `http://127.0.0.1:8001/openapi.json` (or save that JSON to a file).

```bash
uv run python - <<'PY'
import json
from copilot.llm import get_client
from copilot.spec_tools import ask_spec

spec = json.load(open("openapi.json"))
print(ask_spec(get_client(), spec, "Which endpoints can I use to work with tasks, and what does each do?"))
PY
```

The model should call `list_endpoints`, then maybe `describe_endpoint`, then answer.

> Small models sometimes skip tools or write bad arguments. That is normal, and a good reason to keep the error handling.

### 4. Commit

```bash
git add -A && git commit -m "Add OpenAPI tools and one round of tool calling"
```

### Expected structure

```
devdocs-copilot/
├── copilot/
│   ├── __init__.py
│   ├── cli.py
│   ├── llm.py
│   ├── prompts.py
│   ├── qa.py
│   ├── schemas.py
│   ├── spec_tools.py
│   └── tools.py
├── .env.example
├── .gitignore
├── pyproject.toml
└── uv.lock
```

### Checkpoint

The hidden tests check `make_tool`, that your tools read a spec correctly, that unknown tools and bad arguments come back as error text, and that `ask_spec` runs a full round with a fake model: the model asks for a tool, your code runs it, and the result is sent back. Steps 1 to 5 must keep working.
