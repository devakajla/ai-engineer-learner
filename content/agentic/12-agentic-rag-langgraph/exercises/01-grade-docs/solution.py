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
def grade_doc(client, question, doc):
    reply = ask(
        client,
        f"Question: {question}\n\nDocument: {doc}\n\n"
        "Is the document relevant to the question? Answer yes or no.",
    )
    return reply.strip().lower().startswith("yes")


def grade_docs(client, question, docs):
    return [doc for doc in docs if grade_doc(client, question, doc)]
