import json


# Given from earlier exercises. Do not change these.
def run_tool_call(call, functions):
    name = call.function.name
    if name not in functions:
        content = f"error: unknown tool {name}"
    else:
        try:
            content = str(functions[name](**json.loads(call.function.arguments)))
        except Exception as error:
            content = f"error: {error}"
    return {"role": "tool", "tool_call_id": call.id, "content": content}


def message_to_dict(message):
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


# Your task:
def agent_step(client, messages, tools, functions):
    ...
