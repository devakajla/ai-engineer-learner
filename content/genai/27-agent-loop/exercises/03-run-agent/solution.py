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


def agent_step(client, messages, tools, functions):
    response = client.chat.completions.create(model="qwen/qwen3.8-27b", messages=messages, tools=tools)
    message = response.choices[0].message
    new_messages = messages + [message_to_dict(message)]
    if not message.tool_calls:
        return {"done": True, "answer": message.content, "messages": new_messages}
    for call in message.tool_calls:
        new_messages = new_messages + [run_tool_call(call, functions)]
    return {"done": False, "answer": None, "messages": new_messages}


def run_agent(client, question, tools, functions, system="You are a helpful assistant.", max_steps=5):
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": question},
    ]
    for step in range(1, max_steps + 1):
        result = agent_step(client, messages, tools, functions)
        messages = result["messages"]
        if result["done"]:
            return {"answer": result["answer"], "steps": step, "stopped": "done", "messages": messages}
    return {"answer": None, "steps": max_steps, "stopped": "max_steps", "messages": messages}
