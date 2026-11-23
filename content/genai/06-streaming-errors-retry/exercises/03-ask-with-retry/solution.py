def backoff_delays(tries, base=1, cap=30):
    return [min(base * 2**i, cap) for i in range(tries)]


def ask_with_retry(client, messages, max_tries=3, sleep=None):
    if max_tries < 1:
        raise ValueError("max_tries must be at least 1")
    delays = backoff_delays(max_tries - 1)
    last_error = None
    for attempt in range(max_tries):
        try:
            response = client.chat.completions.create(
                model="qwen/qwen3.8-27b",
                messages=messages,
            )
            return response.choices[0].message.content
        except Exception as error:
            last_error = error
            if sleep is not None and attempt < max_tries - 1:
                sleep(delays[attempt])
    raise last_error
