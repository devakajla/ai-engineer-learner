# Step 2 — A system prompt and a chat history

In step 1 every question was alone. A real assistant remembers the chat. You learned that the model remembers nothing, so your code must keep the history and send it each time.

In this step you give Copilot a **personality** (a system prompt) and a **memory** (a history list).

### 1. Add a system prompt

In `copilot/llm.py`, add a constant near the top:

```python
SYSTEM_PROMPT = (
    "You are DevDocs Copilot, an assistant that answers questions about API documentation. "
    "Keep answers short and clear. If you are not sure, say so."
)
```

> Why a constant? The system prompt is part of your product. Keeping it in one named place makes it easy to find, review and improve later. In Level 2 you will version your prompts.

### 2. Add `build_messages`

```python
def build_messages(history, question):
    """System prompt first, then the earlier turns, then the new question."""
    system = {"role": "system", "content": SYSTEM_PROMPT}
    user = {"role": "user", "content": question}
    return [system] + history + [user]
```

Notice that the **history does not contain the system message**. The system message is added fresh every time. This avoids sending it twice.

### 3. Add `chat_turn`

```python
def chat_turn(client, history, question, model=DEFAULT_MODEL):
    """Send one chat turn. Returns (reply, new_history). The history has no system message."""
    messages = build_messages(history, question)
    response = client.chat.completions.create(model=model, messages=messages)
    reply = response.choices[0].message.content
    new_history = history + [
        {"role": "user", "content": question},
        {"role": "assistant", "content": reply},
    ]
    return reply, new_history
```

Why it returns a **new** list and does not change `history`: the caller stays in control of its own data. This makes the function easy to test and hard to break.

Keep `ask` from step 1. It must still work.

### 4. Try it for real

```bash
uv run python - <<'PY'
from copilot.llm import get_client, chat_turn

client = get_client()
history = []
reply, history = chat_turn(client, history, "What is a REST API?")
print(reply)
reply, history = chat_turn(client, history, "Give me a one-line example.")
print(reply)
PY
```

The second answer should make sense *because* the first turn was in the history.

### 5. Commit

```bash
git add -A && git commit -m "Add system prompt and chat history"
```

### Expected structure

```
devdocs-copilot/
├── copilot/
│   ├── __init__.py
│   └── llm.py
├── .env.example
├── .gitignore
├── pyproject.toml
└── uv.lock
```

### Checkpoint

The hidden tests use a fake client. They check that the system prompt is sent first, that the history is sent with each call, that your function does not change the history you pass in, and that the step 1 `ask` function still works.
