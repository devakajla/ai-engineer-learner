# Given from earlier exercises. Do not change these.
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


def manage_memory(client, history, keep_last, max_tokens):
    total = sum(estimate_tokens(m["content"]) for m in history)
    if total <= max_tokens:
        return list(history)
    shorter = summarize_old(client, history, keep_last)
    return trim_to_budget(shorter, max_tokens)
