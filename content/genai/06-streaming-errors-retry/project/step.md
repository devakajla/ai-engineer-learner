# Step 3 — Retries, streaming and a terminal chat

Your Copilot works, but only on a good day. A busy server or a bad network would crash it. In this step you make it **reliable**, and you add a small terminal chat so you can finally *use* it.

### 1. Wait longer after each failure

In `copilot/llm.py`, add `import time` and `import groq` at the top. Then add:

```python
RETRYABLE = (groq.APIConnectionError, groq.RateLimitError, groq.InternalServerError)


def backoff_delays(tries, base=1.0, cap=30.0):
    """Seconds to wait after each failed try: base, 2*base, 4*base ... never more than cap."""
    return [min(base * 2**i, cap) for i in range(tries)]
```

> **Why a tuple of errors?** Only some problems go away by themselves: rate limits, server errors, connection problems (a timeout is a kind of connection error). A wrong key or a bad request will fail every time. Retrying those only wastes time, so they must stop the program right away.

### 2. Retry the model call

```python
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
```

On the last try there is nothing left to retry, so the error is **raised**, not hidden. `base_delay` is a parameter so that tests can pass `0` and not wait.

### 3. A streaming helper

```python
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
```

(In a later step the pieces will be sent to a web page as they arrive.)

### 4. Use the retry in `chat_turn`, and add a timeout to the client

Change `chat_turn` so it calls `complete_with_retry`, and give it two extra parameters, `max_tries=3` and `base_delay=1.0`, that it passes along:

```python
def chat_turn(client, history, question, model=DEFAULT_MODEL, max_tries=3, base_delay=1.0):
    messages = build_messages(history, question)
    reply = complete_with_retry(client, messages, model=model, max_tries=max_tries, base_delay=base_delay)
    ...  # the history part stays as before
```

In `get_client()`, make the client with a timeout: `groq.Groq(api_key=api_key, timeout=30.0)`. (If you used `from groq import Groq` before, `import groq` at the top now makes this simpler.)

### 5. A terminal chat: `copilot/cli.py`

```python
from copilot.llm import chat_turn, get_client


def main():
    client = get_client()
    history = []
    print("DevDocs Copilot. Type 'quit' to stop.")
    while True:
        question = input("You: ").strip()
        if question.lower() in ("quit", "exit"):
            break
        if not question:
            continue
        try:
            reply, history = chat_turn(client, history, question)
        except Exception as error:
            print(f"Sorry, the model call failed: {error}")
            continue
        print(f"Copilot: {reply}")


if __name__ == "__main__":
    main()
```

Notice:
- The loop **catches errors** and keeps going, so one bad call does not end the chat.
- `get_client` and `chat_turn` are imported with `from ... import`. The tests swap them for fakes.

Try it:

```bash
uv run python -m copilot.cli
```

Ask a question, then a follow-up like "explain that more simply". The follow-up works because of the history from step 2.

### 6. Commit

```bash
git add -A && git commit -m "Add retries, streaming helper and terminal chat"
```

### Expected structure

```
devdocs-copilot/
├── copilot/
│   ├── __init__.py
│   ├── cli.py
│   └── llm.py
├── .env.example
├── .gitignore
├── pyproject.toml
└── uv.lock
```

### Checkpoint

The hidden tests use fake clients that fail on purpose. They check the backoff list, that a flaky call is retried and then works, that other errors are **not** retried, that the streaming helper joins pieces, that `chat_turn` retries, and that the terminal chat survives an error.
