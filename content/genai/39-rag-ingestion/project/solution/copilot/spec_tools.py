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
