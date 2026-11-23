def multi_query(client, question, n=3):
    prompt = f"Write {n} different ways to ask this question, one per line, no numbering:\n{question}"
    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_completion_tokens=200,
    )
    seen = [question.lower()]
    queries = [question]
    for line in response.choices[0].message.content.splitlines():
        text = line.strip().lstrip("-*• ").strip()
        if text and text.lower() not in seen:
            seen.append(text.lower())
            queries.append(text)
    return queries[: n + 1]
