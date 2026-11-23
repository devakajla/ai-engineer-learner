def pick_label(reply, labels):
    cleaned = reply.strip().lower().strip(".")
    if cleaned in labels:
        return cleaned
    return "unknown"


def classify(client, text, labels):
    prompt = (
        f"Classify the text as one of: {', '.join(labels)}. Answer with only the label.\n\n"
        f"Text: {text}"
    )
    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return pick_label(response.choices[0].message.content, labels)
