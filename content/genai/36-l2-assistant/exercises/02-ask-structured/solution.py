import json

from pydantic import BaseModel, Field, ValidationError


# Given from Level 2. Do not change these.
def render(template, values):
    try:
        return template.format(**values)
    except KeyError as e:
        raise ValueError(f"missing variable: {e.args[0]}")


def get_prompt(registry, name, version=None):
    versions = registry[name]
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


def render_prompt(registry, name, values, version=None):
    return render(get_prompt(registry, name, version), values)


def examples_to_messages(examples):
    messages = []
    for inp, out in examples:
        messages.append({"role": "user", "content": inp})
        messages.append({"role": "assistant", "content": out})
    return messages


# Given from exercise 1 and lesson 10. Do not change these.
def prepare_messages(registry, name, values, question, examples=None, version=None):
    system = render_prompt(registry, name, values, version)
    messages = [{"role": "system", "content": system}]
    messages = messages + examples_to_messages(examples or [])
    return messages + [{"role": "user", "content": question}]


class Ticket(BaseModel):
    title: str = Field(min_length=1)
    priority: int = Field(ge=1, le=5)
    tags: list[str] = []


def check_reply(model_class, text):
    try:
        return model_class.model_validate_json(text), None
    except ValidationError as error:
        return None, str(error)


# Exercise 2 (given in exercise 3).
def ask_structured(client, messages, model_class, max_tries=3):
    for _ in range(max_tries):
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0,
        )
        reply = response.choices[0].message.content
        result, error = check_reply(model_class, reply)
        if error is None:
            return result
        messages = messages + [
            {"role": "assistant", "content": reply},
            {"role": "user", "content": f"Your reply was invalid: {error}\nFix it and reply with JSON only."},
        ]
    raise ValueError("could not get a valid reply")
