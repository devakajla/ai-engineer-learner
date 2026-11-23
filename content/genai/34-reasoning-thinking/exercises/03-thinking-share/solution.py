def estimate_tokens(text):
    return (len(text) + 3) // 4


def thinking_share(thinking, output_tokens):
    if output_tokens == 0:
        return 0.0
    thinking_tokens = estimate_tokens(thinking)
    return round(min(thinking_tokens / output_tokens, 1.0), 2)
