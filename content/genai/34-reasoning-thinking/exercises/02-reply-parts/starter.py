# Given from the previous exercise. Do not change it.
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


# Your task:
def reply_parts(message):
    ...
