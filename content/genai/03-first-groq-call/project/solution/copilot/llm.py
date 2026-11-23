import os

DEFAULT_MODEL = "qwen/qwen3.8-27b"


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
