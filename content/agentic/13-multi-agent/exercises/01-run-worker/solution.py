# Given. Do not change ask.
def ask(client, prompt, system=None, temperature=0):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b", messages=messages, temperature=temperature
    )
    return response.choices[0].message.content.strip()


def run_worker(client, name, worker, task, context=""):
    prompt = task if not context else f"{task}\n\nWork so far:\n{context}"
    return {"worker": name, "output": ask(client, prompt, system=worker["system"])}


def format_results(results):
    return "\n".join(f"{r['worker']}: {r['output']}" for r in results)
