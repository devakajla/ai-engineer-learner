# Given from earlier exercises. Do not change these.
def ask(client, prompt, system=None, temperature=0):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b", messages=messages, temperature=temperature
    )
    return response.choices[0].message.content.strip()


def route(client, question, routes):
    labels = ", ".join(routes)
    reply = ask(
        client,
        f"Classify the question into one of these labels: {labels}. "
        f"Answer with only the label.\n\nQuestion: {question}",
    )
    label = reply.lower().strip(".")
    if label not in routes:
        label = "other"
    answer = ask(client, question, system=routes[label])
    return {"label": label, "answer": answer}
