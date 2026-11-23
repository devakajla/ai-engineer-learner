# Step 7 — Memory that fits

Copilot's chat sends the **whole** history on every turn. After a long chat it gets slow and expensive, and one day it hits the context limit. In this step you add memory rules.

A good rule to remember: **trim what you send, not what you store.** The full history stays in your list (a UI can show it, a log can keep it). You only decide how much of it goes to the model.

### 1. Pure memory rules: `copilot/memory.py`

These functions never call the model, so they are easy to test.

```python
"""Rules for what to keep from a long chat. Pure functions, no model calls."""


def estimate_tokens(text):
    """About 4 characters per token, rounded up."""
    return (len(text) + 3) // 4


def trim_last(history, n):
    """The last n messages, as a new list."""
    if n <= 0:
        return []
    return history[-n:]


def trim_to_budget(history, max_tokens):
    """The newest messages that fit in max_tokens, oldest first. Stops at the first one that does not fit."""
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
```

### 2. Summary memory: `copilot/summary.py`

This one calls the model, so it lives in its own file. It reuses `complete_with_retry`, so network errors are retried for free.

```python
from copilot.llm import DEFAULT_MODEL, complete_with_retry


def summarize_old(client, history, keep_last, model=DEFAULT_MODEL, base_delay=1.0):
    """Replace all but the last keep_last messages by one summary message."""
    if len(history) <= keep_last:
        return list(history)
    cut = len(history) - keep_last
    old = history[:cut]
    recent = history[cut:]
    transcript = "\n".join(f"{m['role']}: {m['content']}" for m in old)
    prompt = "Summarize this conversation in 2 sentences:\n" + transcript
    summary = complete_with_retry(
        client,
        [{"role": "user", "content": prompt}],
        model=model,
        base_delay=base_delay,
    )
    return [{"role": "user", "content": "Summary of the earlier chat: " + summary}] + recent
```

Why two files? `summary.py` imports from `llm.py`. If `memory.py` imported from `llm.py` too, and `llm.py` imports `memory.py` (next step), the two files would import each other, which Python does not like. Pure functions in one file, model-calling code in another keeps the arrows pointing one way.

### 3. Use the budget in `chat_turn`

At the top of `copilot/llm.py` add `from copilot.memory import trim_to_budget`. Then change `chat_turn`:

```python
def chat_turn(client, history, question, model=DEFAULT_MODEL, max_tries=3, base_delay=1.0, max_history_tokens=None):
    """Send one chat turn. Returns (reply, new_history). The history has no system message.

    With max_history_tokens, only the newest messages that fit are SENT. The returned history stays complete.
    """
    sent = history if max_history_tokens is None else trim_to_budget(history, max_history_tokens)
    messages = build_messages(sent, question)
    ...  # the rest is the same: call, then build new_history from the FULL history
```

The last part is important: `new_history` is built from `history` (the full one), not from `sent`.

### 4. Use it in the terminal chat

In `copilot/cli.py`, pass a budget: `chat_turn(client, history, question, max_history_tokens=2000)`. Chat for a while. Early messages will drop out of what the model sees, but not out of `history`.

### 5. Commit

```bash
git add -A && git commit -m "Add chat memory: token budget trimming and summaries"
```

### Expected structure

```
devdocs-copilot/
├── copilot/
│   ├── __init__.py
│   ├── cli.py
│   ├── llm.py
│   ├── memory.py
│   ├── prompts.py
│   ├── qa.py
│   ├── schemas.py
│   ├── spec_tools.py
│   ├── summary.py
│   └── tools.py
├── .env.example
├── .gitignore
├── pyproject.toml
└── uv.lock
```

### Checkpoint

The hidden tests check `trim_last` (including `n = 0`), `trim_to_budget`, `summarize_old` (including `keep_last = 0` and a short history), and that `chat_turn` sends only the trimmed history while still returning the full one. Steps 1 to 6 must keep working.
