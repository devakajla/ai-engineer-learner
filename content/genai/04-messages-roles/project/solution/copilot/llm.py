import os

DEFAULT_MODEL = "qwen/qwen3.8-27b"

SYSTEM_PROMPT = (
    "You are DevDocs Copilot, an assistant that answers questions about API documentation. "
    "Keep answers short and clear. If you are not sure, say so."
)


def get_client():
    """Make the Groq client. Fail early, with a clear message, if the key is missing."""
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set. Run: export GROQ_API_KEY=...")
    from groq import Groq

    return Groq(api_key=api_key)


def ask(client, question, model=DEFAULT_MODEL):
    messages = [{"role": "user", "content": question}]
    response = client.chat.completions.create(model=model, messages=messages)
    return response.choices[0].message.content


def build_messages(history, question):
    """System prompt first, then the earlier turns, then the new question."""
    system = {"role": "system", "content": SYSTEM_PROMPT}
    user = {"role": "user", "content": question}
    return [system] + history + [user]


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
