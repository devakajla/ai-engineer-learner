def few_shot_messages(system, examples, question):
    messages = [{"role": "system", "content": system}]
    for inp, out in examples:
        messages.append({"role": "user", "content": inp})
        messages.append({"role": "assistant", "content": out})
    messages.append({"role": "user", "content": question})
    return messages
