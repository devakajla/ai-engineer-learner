# Step 1 — Project setup and your first LLM helper

You are starting **DevDocs Copilot**: a tool that answers questions about API documentation and shows where each answer came from. By the end of this track it will be a real project you can put on your resume.

This first step is small but important. You set up the project the way professional teams do, and you write one tiny function that talks to Groq.

### 1. Create the project

```bash
mkdir -p ~/Projects/devdocs-copilot
cd ~/Projects/devdocs-copilot
git init
```

Create `pyproject.toml`:

```toml
[project]
name = "devdocs-copilot"
version = "0.1.0"
description = "Answers questions about API docs, with sources"
requires-python = ">=3.12"
dependencies = []
```

Then add the Groq SDK. `uv` writes it into `pyproject.toml` for you:

```bash
uv add groq
```

### 2. Keep secrets out of git

Create `.gitignore`:

```
.venv/
__pycache__/
.env
```

Create `.env.example`. This file shows **which** variables the project needs, but holds **no real secret**. Anyone who clones the project copies it to `.env` and fills it in.

```
GROQ_API_KEY=
```

> Why two files? `.env` holds the real key, and git ignores it. `.env.example` is safe to commit. Never put a real key in `.env.example`.

In your terminal, set the real key for this session:

```bash
export GROQ_API_KEY="gsk_your_key_here"
```

### 3. Write `copilot/llm.py`

Create an empty `copilot/__init__.py` (it makes `copilot` a package). Then create `copilot/llm.py`:

```python
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
```

Why it is written this way:

- **`DEFAULT_MODEL` is a constant at the top.** Models get renamed and replaced. You change one line, not ten.
- **`get_client()` checks the key first.** A clear error message ("GROQ_API_KEY is not set") is much better than a confusing error from deep inside the SDK.
- **`from groq import Groq` is inside the function.** Code that never needs a real client (like tests) does not need the SDK to load.
- **`ask` takes the `client` as an argument.** You can test it with a fake client and no internet. Every later step builds on this.

### 4. Try it for real

```bash
uv run python -c "from copilot.llm import get_client, ask; print(ask(get_client(), 'Say hello in 5 words'))"
```

You should see an answer from the model. If you get `GROQ_API_KEY is not set`, export the key in this same terminal.

### 5. Commit

```bash
git add -A && git commit -m "Set up DevDocs Copilot with a Groq helper"
```

Check with `git status` that `.env` is **not** listed as a new file.

### Expected structure

```
devdocs-copilot/
├── copilot/
│   ├── __init__.py
│   └── llm.py
├── .env.example
├── .gitignore
├── README.md        (optional)
├── pyproject.toml
└── uv.lock
```

### Checkpoint

The hidden tests check that `groq` is a dependency, that `.env` is git-ignored, that `.env.example` has no real key, that `get_client()` fails with a clear message when the key is missing, and that `ask()` sends one user message and returns the text. The tests use a fake client, so they do not call Groq.
