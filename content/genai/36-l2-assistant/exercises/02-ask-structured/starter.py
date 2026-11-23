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


# Your task:
def ask_structured(client, messages, model_class, max_tries=3):
    ...
