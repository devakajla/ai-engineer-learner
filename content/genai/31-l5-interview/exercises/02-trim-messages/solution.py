# Given from earlier exercises. Do not change these.
def estimate_tokens(text):
    return (len(text) + 3) // 4


def trim_messages(messages, max_tokens):
    kept = []
    used = 0
    start = 0
    if messages and messages[0]["role"] == "system":
        first = messages[0]
        used = estimate_tokens(first["content"] or "")
        kept.append(first)
        start = 1
    newest = []
    for message in reversed(messages[start:]):
        cost = estimate_tokens(message["content"] or "")
        if used + cost > max_tokens:
            break
        newest.append(message)
        used += cost
    newest.reverse()
    return kept + newest
