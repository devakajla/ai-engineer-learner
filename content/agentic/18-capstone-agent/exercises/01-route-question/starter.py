# Given from earlier lessons. Do not change these.
def ask(client, prompt, system=None, temperature=0):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b", messages=messages, temperature=temperature
    )
    return response.choices[0].message.content.strip()


# Your task:
ROUTES = ["docs", "tasks", "chat"]


def route_question(client, question):
    ...
