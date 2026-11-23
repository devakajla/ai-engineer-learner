def build_messages(system, user):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})
    return messages


def ask_with(client, question, temperature=0.7, max_output_tokens=500, stop=None):
    params = {
        "model": "qwen/qwen3.8-27b",
        "messages": build_messages("", question),
        "temperature": temperature,
        "max_completion_tokens": max_output_tokens,
    }
    if stop is not None:
        params["stop"] = stop
    response = client.chat.completions.create(**params)
    return response.choices[0].message.content
