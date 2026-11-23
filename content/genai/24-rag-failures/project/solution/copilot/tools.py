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
