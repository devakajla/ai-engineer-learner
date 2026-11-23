import os
import time

import groq

DEFAULT_MODEL = "qwen/qwen3.8-27b"

SYSTEM_PROMPT = (
    "You are DevDocs Copilot, an assistant that answers questions about API documentation. "
    "Keep answers short and clear. If you are not sure, say so."
)

# Problems that can go away by themselves. Anything else (bad key, bad request) is a bug to fix.
RETRYABLE = (groq.APIConnectionError, groq.RateLimitError, groq.InternalServerError)


def get_client():
    """Make the Groq client. Fail early, with a clear message, if the key is missing."""
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set. Run: export GROQ_API_KEY=...")
    return groq.Groq(api_key=api_key, timeout=30.0)


def ask(client, question, model=DEFAULT_MODEL):
    messages = [{"role": "user", "content": question}]
    response = client.chat.completions.create(model=model, messages=messages)
    return response.choices[0].message.content


def build_messages(history, question):
    """System prompt first, then the earlier turns, then the new question."""
    system = {"role": "system", "content": SYSTEM_PROMPT}
    user = {"role": "user", "content": question}
    return [system] + history + [user]


def backoff_delays(tries, base=1.0, cap=30.0):
    """Seconds to wait after each failed try: base, 2*base, 4*base ... never more than cap."""
    return [min(base * 2**i, cap) for i in range(tries)]


def complete_with_retry(client, messages, model=DEFAULT_MODEL, max_tries=3, base_delay=1.0):
    """Call the model. Retry problems that can go away, with exponential backoff."""
    if max_tries < 1:
        raise ValueError("max_tries must be at least 1")
    delays = backoff_delays(max_tries, base_delay)
    for attempt in range(max_tries):
        try:
            response = client.chat.completions.create(model=model, messages=messages)
            return response.choices[0].message.content
        except RETRYABLE:
            if attempt == max_tries - 1:
                raise
            time.sleep(delays[attempt])


def stream_answer(client, messages, model=DEFAULT_MODEL):
    """Stream the answer and return the full text."""
    stream = client.chat.completions.create(model=model, messages=messages, stream=True)
    pieces = []
    for chunk in stream:
        if not chunk.choices:
            continue
        piece = chunk.choices[0].delta.content
        if piece:
            pieces.append(piece)
    return "".join(pieces)


def chat_turn(client, history, question, model=DEFAULT_MODEL, max_tries=3, base_delay=1.0):
    """Send one chat turn. Returns (reply, new_history). The history has no system message."""
    messages = build_messages(history, question)
    reply = complete_with_retry(client, messages, model=model, max_tries=max_tries, base_delay=base_delay)
    new_history = history + [
        {"role": "user", "content": question},
        {"role": "assistant", "content": reply},
    ]
    return reply, new_history
