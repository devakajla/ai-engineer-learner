# Given from the previous exercise. Do not change it.
def backoff_delays(tries, base=1, cap=30):
    return [min(base * 2**i, cap) for i in range(tries)]


# Your task:
def ask_with_retry(client, messages, max_tries=3, sleep=None):
    ...
