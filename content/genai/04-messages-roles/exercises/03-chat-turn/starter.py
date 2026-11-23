# Given from the previous exercise. Do not change it.
def add_turn(history, role, content):
    return history + [{"role": role, "content": content}]


# Your task:
def chat_turn(client, history, question, model="qwen/qwen3.8-27b"):
    ...
