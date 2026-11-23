SETTINGS = {
    "extract": {"temperature": 0, "max_completion_tokens": 200},
    "chat": {"temperature": 0.7, "max_completion_tokens": 500},
    "creative": {"temperature": 1.0, "max_completion_tokens": 800},
}


def estimate_tokens(text):
    return (len(text) + 3) // 4


def fits(prompt_tokens, max_output, context_limit):
    return prompt_tokens + max_output <= context_limit


def estimate_cost(input_tokens, output_tokens, input_price, output_price):
    input_cost = input_tokens / 1_000_000 * input_price
    output_cost = output_tokens / 1_000_000 * output_price
    return round(input_cost + output_cost, 6)


def build_messages(system, user):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})
    return messages


def add_turn(history, role, content):
    return history + [{"role": role, "content": content}]


def build_params(task):
    if task not in SETTINGS:
        raise ValueError(f"unknown task: {task}")
    return dict(SETTINGS[task])


def usage_summary(response):
    usage = response.usage
    return {
        "input": usage.prompt_tokens,
        "output": usage.completion_tokens,
        "total": usage.total_tokens,
    }


def backoff_delays(tries, base=1, cap=30):
    return [min(base * 2**i, cap) for i in range(tries)]


def chat(client, history, question, task="chat", max_tries=3, sleep=None):
    if max_tries < 1:
        raise ValueError("max_tries must be at least 1")
    params = build_params(task)
    messages = add_turn(history, "user", question)
    delays = backoff_delays(max_tries - 1)
    last_error = None
    for attempt in range(max_tries):
        try:
            response = client.chat.completions.create(
                model="qwen/qwen3.8-27b", messages=messages, **params
            )
            reply = response.choices[0].message.content
            return reply, add_turn(messages, "assistant", reply)
        except Exception as error:
            last_error = error
            if sleep is not None and attempt < max_tries - 1:
                sleep(delays[attempt])
    raise last_error
