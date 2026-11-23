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
    reply = ask(
        client,
        "Pick one route for this question. docs = questions about the API documentation. "
        "tasks = questions about the user's own tasks. chat = greetings and small talk. "
        "Reply with one word: docs, tasks or chat.\n\nQuestion: " + question,
    )
    word = reply.strip().strip(".!\"' `").lower()
    return word if word in ROUTES else "docs"
