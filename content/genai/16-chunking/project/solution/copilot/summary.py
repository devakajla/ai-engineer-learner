from copilot.llm import DEFAULT_MODEL, complete_with_retry


def summarize_old(client, history, keep_last, model=DEFAULT_MODEL, base_delay=1.0):
    """Replace all but the last keep_last messages by one summary message."""
    if len(history) <= keep_last:
        return list(history)
    cut = len(history) - keep_last
    old = history[:cut]
    recent = history[cut:]
    transcript = "\n".join(f"{m['role']}: {m['content']}" for m in old)
    prompt = "Summarize this conversation in 2 sentences:\n" + transcript
    summary = complete_with_retry(
        client,
        [{"role": "user", "content": prompt}],
        model=model,
        base_delay=base_delay,
    )
    return [{"role": "user", "content": "Summary of the earlier chat: " + summary}] + recent
