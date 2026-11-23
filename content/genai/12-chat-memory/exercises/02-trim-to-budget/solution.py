def estimate_tokens(text):
    return (len(text) + 3) // 4


def trim_to_budget(history, max_tokens):
    kept = []
    total = 0
    for message in reversed(history):
        tokens = estimate_tokens(message["content"])
        if total + tokens > max_tokens:
            break
        kept.append(message)
        total += tokens
    kept.reverse()
    return kept
