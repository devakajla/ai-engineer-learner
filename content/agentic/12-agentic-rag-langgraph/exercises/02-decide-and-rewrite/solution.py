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


# Your task:
def decide_next(state):
    if state["relevant"]:
        return "answer"
    if state["tries"] >= state["max_tries"]:
        return "give_up"
    return "rewrite"


def rewrite_question(client, question):
    return ask(
        client,
        "Rewrite this question so a search engine finds better results. "
        "Reply with the new question only.\n\n" + question,
    )
