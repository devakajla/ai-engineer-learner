# Step 5 — Answers with a fixed shape

Right now Copilot returns a loose piece of text. A real product needs **data**: an answer, whether it was found, how sure the model is, and the exact sentence it used. With that, a web page (or a later step) can show a source, or hide a weak answer.

In this step Copilot returns a checked **`Answer`** object. If the model sends bad JSON, Copilot sends the error back and tries again (the repair loop from lesson 10).

### 1. The shape: `copilot/schemas.py`

```python
from typing import Literal

from pydantic import BaseModel


class Answer(BaseModel):
    """The shape of every answer Copilot gives back."""

    answer: str
    found: bool
    confidence: Literal["high", "medium", "low"]
    quote: str = ""
```

`Literal` allows only the three listed words. `quote` is optional.

Add Pydantic to the project: `uv add pydantic`.

### 2. A prompt that asks for this shape

Add a new prompt called `qa_json` in `copilot/prompts.py`, next to `qa`. Keep `qa` as it is: step 4 must still work.

```python
    "qa_json": {
        "v1": (
            "Answer only from the text between the tags. "
            "Reply with JSON only, in exactly this shape:\n"
            '{{"answer": "...", "found": true, "confidence": "high", "quote": "..."}}\n'
            "Rules: found is false when the answer is not in the text (then answer is \"I don't know\" "
            'and quote is ""). confidence is one of high, medium, low. '
            "quote is the exact sentence from the text that supports the answer.\n\n"
            "<document>\n{document}\n</document>\n\n"
            "Question: {question}"
        ),
    },
```

Look at the **doubled braces** in `{{"answer": ...}}`. The template is filled with `.format`, so a real `{` must be written `{{` (lesson 8).

### 3. Let `complete_with_retry` ask for JSON mode

In `copilot/llm.py`, add a `response_format=None` parameter to `complete_with_retry`. Only send it when it is not `None`:

```python
def complete_with_retry(client, messages, model=DEFAULT_MODEL, max_tries=3, base_delay=1.0, response_format=None):
    ...
    options = {}
    if response_format is not None:
        options["response_format"] = response_format
    for attempt in range(max_tries):
        try:
            response = client.chat.completions.create(model=model, messages=messages, **options)
            ...
```

Everything else in the function stays the same. Old calls still work, because the default is `None`.

### 4. `answer_structured` in `copilot/qa.py`

Add imports (`from pydantic import ValidationError` and `from copilot.schemas import Answer`), then:

```python
def answer_structured(client, question, document, max_tries=3, model=DEFAULT_MODEL, base_delay=1.0):
    """Answer with a validated Answer. If the reply is invalid, send the error back and try again."""
    template = get_prompt("qa_json")
    prompt = render(template, {"document": document.strip(), "question": question.strip()})
    messages = build_messages([], prompt)
    last_error = None
    for _ in range(max_tries):
        reply = complete_with_retry(
            client,
            messages,
            model=model,
            base_delay=base_delay,
            response_format={"type": "json_object"},
        )
        try:
            return Answer.model_validate_json(reply)
        except ValidationError as error:
            last_error = error
            messages = messages + [
                {"role": "assistant", "content": reply},
                {"role": "user", "content": f"Your reply was invalid: {error}\nFix it and reply with JSON only."},
            ]
    raise ValueError("could not get a valid answer") from last_error
```

Two different loops, two different jobs. `complete_with_retry` retries **network problems**. `answer_structured` retries **bad content**. Keep them apart.

### 5. Try it for real

```bash
uv run python - <<'PY'
from copilot.llm import get_client
from copilot.qa import answer_structured

doc = "TaskFlow has a GET /tasks endpoint. It returns all tasks. A task has an id, a title and a done flag."
client = get_client()
print(answer_structured(client, "How do I list all tasks?", doc))
print(answer_structured(client, "How do I delete a task?", doc))
PY
```

The second one should have `found=False`.

### 6. Commit

```bash
git add -A && git commit -m "Return validated Answer objects with a repair loop"
```

### Expected structure

```
devdocs-copilot/
├── copilot/
│   ├── __init__.py
│   ├── cli.py
│   ├── llm.py
│   ├── prompts.py
│   ├── qa.py
│   └── schemas.py
├── .env.example
├── .gitignore
├── pyproject.toml
└── uv.lock
```

### Checkpoint

The hidden tests check the `Answer` model (its fields and the `Literal` values), that `answer_structured` asks for JSON mode, returns a valid `Answer`, repairs an invalid reply by sending the error back, and gives up with a clear error after `max_tries`. Steps 1 to 4 must keep working.
