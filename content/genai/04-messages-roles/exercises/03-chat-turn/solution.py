def add_turn(history, role, content):
    return history + [{"role": role, "content": content}]


def chat_turn(client, history, question, model="qwen/qwen3.8-27b"):
    messages = add_turn(history, "user", question)
    response = client.chat.completions.create(model=model, messages=messages)
    reply = response.choices[0].message.content
    new_history = add_turn(messages, "assistant", reply)
    return reply, new_history
