import json


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


def chat_with_tools(client, messages, tools, functions):
    response = client.chat.completions.create(model="qwen/qwen3.8-27b", messages=messages, tools=tools)
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
    tool_messages = [run_tool_call(call, functions) for call in message.tool_calls]
    next_messages = messages + [assistant_message] + tool_messages
    response = client.chat.completions.create(model="qwen/qwen3.8-27b", messages=next_messages, tools=tools)
    return response.choices[0].message.content
