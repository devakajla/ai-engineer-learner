"""Rules for what to keep from a long chat. Pure functions, no model calls."""


def estimate_tokens(text):
    """About 4 characters per token, rounded up."""
    return (len(text) + 3) // 4


def trim_last(history, n):
    """The last n messages, as a new list."""
    if n <= 0:
        return []
    return history[-n:]


def trim_to_budget(history, max_tokens):
    """The newest messages that fit in max_tokens, oldest first. Stops at the first one that does not fit."""
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
