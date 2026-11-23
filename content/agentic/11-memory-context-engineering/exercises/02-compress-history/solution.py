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
def compress_history(client, messages, keep_last=4):
    if len(messages) <= keep_last:
        return messages
    older = messages[:-keep_last] if keep_last else messages
    recent = messages[-keep_last:] if keep_last else []
    transcript = "\n".join(f"{m['role']}: {m['content']}" for m in older)
    summary = ask(client, "Summarise this chat in 2 short sentences. Keep names and decisions.\n\n" + transcript)
    return [{"role": "system", "content": "Summary of the earlier chat: " + summary}] + recent
