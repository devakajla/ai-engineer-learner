def split_thinking(text):
    start = text.find("<think>")
    if start == -1:
        return "", text.strip()
    after_open = start + len("<think>")
    end = text.find("</think>", after_open)
    if end == -1:
        return text[after_open:].strip(), ""
    thinking = text[after_open:end].strip()
    answer = text[end + len("</think>"):].strip()
    return thinking, answer


def reply_parts(message):
    content = message.content or ""
    reasoning = getattr(message, "reasoning", None)
    if reasoning and reasoning.strip():
        return {"thinking": reasoning.strip(), "answer": content.strip()}
    thinking, answer = split_thinking(content)
    return {"thinking": thinking, "answer": answer}
