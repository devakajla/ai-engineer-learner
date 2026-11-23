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


# Your task:
def prepare_messages(registry, name, values, question, examples=None, version=None):
    ...
