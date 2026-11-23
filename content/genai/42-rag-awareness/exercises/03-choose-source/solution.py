def choose_source(client, question, sources):
    lines = [name + ": " + description for name, description in sources.items()]
    system = (
        "Pick the one source that best fits the question. "
        "Reply with only the source name, or none.\n" + "\n".join(lines)
    )
    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": question},
        ],
        temperature=0,
    )
    name = response.choices[0].message.content.strip().lower().strip(".")
    if name in sources:
        return name
    return None
