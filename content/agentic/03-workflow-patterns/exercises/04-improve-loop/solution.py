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


def improve_loop(client, task, max_rounds=3):
    draft = ask(client, task)
    revisions = 0
    while True:
        verdict = ask(
            client,
            f"Task: {task}\n\nDraft:\n{draft}\n\n"
            "If the draft is good, reply exactly OK. Otherwise reply with one short sentence of feedback.",
        )
        if verdict.rstrip(".").upper() == "OK":
            return {"text": draft, "rounds": revisions, "accepted": True}
        if revisions == max_rounds:
            return {"text": draft, "rounds": revisions, "accepted": False}
        draft = ask(
            client,
            f"Task: {task}\n\nDraft:\n{draft}\n\nFeedback: {verdict}\n\n"
            "Rewrite the draft to fix the feedback. Reply with the new draft only.",
        )
        revisions += 1
