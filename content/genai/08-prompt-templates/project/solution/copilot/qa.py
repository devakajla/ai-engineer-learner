from copilot.llm import DEFAULT_MODEL, build_messages, complete_with_retry
from copilot.prompts import get_prompt, render


def answer_from_text(client, question, document, version=None, model=DEFAULT_MODEL, base_delay=1.0):
    """Answer a question using only the given document text."""
    template = get_prompt("qa", version)
    prompt = render(template, {"document": document.strip(), "question": question.strip()})
    messages = build_messages([], prompt)
    return complete_with_retry(client, messages, model=model, base_delay=base_delay)
