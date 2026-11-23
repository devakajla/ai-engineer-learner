def rewrite_question(client, history, question):
    if not history:
        return question
    transcript = "\n".join(f"{m['role']}: {m['content']}" for m in history)
    prompt = (
        "Rewrite the last question so it can be understood without the chat. "
        "Reply with the question only.\n\n"
        f"Chat:\n{transcript}\n\nLast question: {question}"
    )
    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_completion_tokens=100,
    )
    return response.choices[0].message.content.strip()
