# Given from lesson 4. Do not change it.
def build_messages(system, user):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})
    return messages


# Your task:
def ask_with(client, question, temperature=0.7, max_output_tokens=500, stop=None):
    ...
