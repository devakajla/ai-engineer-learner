import json


def run_tool_call(call, functions):
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
                content = str(functions[name](**args))
            except Exception as error:
                content = f"error: {error}"
    return {"role": "tool", "tool_call_id": call.id, "content": content}
