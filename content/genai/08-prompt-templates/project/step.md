# Step 4 — Prompts live in one place, with versions

Copilot can chat, but it does not yet answer questions **about documents**. This step teaches it the first, simple way: you hand it a piece of text, and it answers only from that text. (Later, in the RAG level, the text will be found automatically.)

You will also fix a habit now that saves you pain later: **prompts do not belong inside functions**. They live in one file, with versions.

### 1. Create `copilot/prompts.py`

```python
"""All prompts live here, with versions. Never scatter prompt text through the code."""

PROMPTS = {
    "qa": {
        "v1": "Document:\n{document}\n\nQuestion: {question}",
        "v2": (
            "Answer only from the text between the tags. "
            "If the answer is not there, reply exactly: I don't know.\n\n"
            "<document>\n{document}\n</document>\n\n"
            "Question: {question}"
        ),
    },
}
```

`v1` is the naive version. `v2` adds the three patterns from lesson 7: **delimiters**, **"answer only from the text"**, and an **exact "I don't know" reply**. Keep both. Old versions are your safety net, and later your baseline for comparing.

Now add the two helpers:

```python
def get_prompt(name, version=None):
    """Return the template text. Without a version, return the latest one (highest number)."""
    versions = PROMPTS[name]
    if version is not None:
        return versions[version]
    best_name = None
    best_number = -1
    for version_name in versions:
        number = int(version_name[1:])
        if number > best_number:
            best_name = version_name
            best_number = number
    return versions[best_name]


def render(template, values):
    """Fill a template. Raise a clear error when a value is missing."""
    try:
        return template.format(**values)
    except KeyError as e:
        raise ValueError(f"missing variable: {e.args[0]}")
```

The version numbers are compared as **numbers**, so `v10` will correctly come after `v2`.

### 2. Create `copilot/qa.py`

```python
from copilot.llm import DEFAULT_MODEL, build_messages, complete_with_retry
from copilot.prompts import get_prompt, render


def answer_from_text(client, question, document, version=None, model=DEFAULT_MODEL, base_delay=1.0):
    """Answer a question using only the given document text."""
    template = get_prompt("qa", version)
    prompt = render(template, {"document": document.strip(), "question": question.strip()})
    messages = build_messages([], prompt)
    return complete_with_retry(client, messages, model=model, base_delay=base_delay)
```

Everything is built from pieces you already have: the template, the system prompt from step 2, and the retrying call from step 3.

### 3. Try it for real

```bash
uv run python - <<'PY'
from copilot.llm import get_client
from copilot.qa import answer_from_text

doc = "TaskFlow has a GET /tasks endpoint. It returns all tasks. A task has an id, a title and a done flag."
client = get_client()
print(answer_from_text(client, "How do I list all tasks?", doc))
print(answer_from_text(client, "How do I delete a task?", doc))   # should say: I don't know.
PY
```

The second question is not answered in the text. A good prompt makes the model say so, instead of guessing. Try the same with `version="v1"` and compare.

### 4. Commit

```bash
git add -A && git commit -m "Add versioned prompts and answer_from_text"
```

### Expected structure

```
devdocs-copilot/
├── copilot/
│   ├── __init__.py
│   ├── cli.py
│   ├── llm.py
│   ├── prompts.py
│   └── qa.py
├── .env.example
├── .gitignore
├── pyproject.toml
└── uv.lock
```

### Checkpoint

The hidden tests check that both prompt versions exist and that the latest one has the delimiters and the "I don't know" rule, that `render` fills values and reports a missing one, that version numbers compare as numbers, and that `answer_from_text` sends your document and question to the model after the system prompt. Steps 1 to 3 must keep working.
