from pydantic import ValidationError

from copilot.llm import DEFAULT_MODEL, build_messages, complete_with_retry
from copilot.prompts import get_prompt, render
from copilot.schemas import Answer


def answer_from_text(client, question, document, version=None, model=DEFAULT_MODEL, base_delay=1.0):
    """Answer a question using only the given document text."""
    template = get_prompt("qa", version)
    prompt = render(template, {"document": document.strip(), "question": question.strip()})
    messages = build_messages([], prompt)
    return complete_with_retry(client, messages, model=model, base_delay=base_delay)


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
