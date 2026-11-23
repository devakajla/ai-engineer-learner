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


def run_chain(client, steps, text):
    outputs = []
    current = text
    for step in steps:
        current = ask(client, step.replace("{input}", current))
        outputs.append(current)
    return {"result": current, "outputs": outputs}
