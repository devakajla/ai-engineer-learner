def ask(client, question, model="qwen/qwen3.8-27b"):
    messages = [{"role": "user", "content": question}]
    response = client.chat.completions.create(model=model, messages=messages)
    return response.choices[0].message.content
