def estimate_tokens(text):
    return (len(text) + 3) // 4


def trim_messages(messages, max_tokens):
    system = []
    rest = messages
    total = 0
    if messages and messages[0]["role"] == "system":
        system = [messages[0]]
        rest = messages[1:]
        total = estimate_tokens(messages[0]["content"])
    kept = []
    for message in reversed(rest):
        tokens = estimate_tokens(message["content"])
        if total + tokens > max_tokens:
            break
        kept.append(message)
        total += tokens
    kept.reverse()
    return system + kept
