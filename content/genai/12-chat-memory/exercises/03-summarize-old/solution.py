def summarize_old(client, history, keep_last):
    if len(history) <= keep_last:
        return list(history)
    cut = len(history) - keep_last
    old = history[:cut]
    recent = history[cut:]
    transcript = "\n".join(f"{m['role']}: {m['content']}" for m in old)
    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[{"role": "user", "content": "Summarize this conversation in 2 sentences:\n" + transcript}],
        temperature=0,
    )
    summary = response.choices[0].message.content
    return [{"role": "user", "content": "Summary of the earlier chat: " + summary}] + recent
