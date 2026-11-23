import re


def split_requirement(text):
    match = re.match(r"^\s*([A-Za-z0-9_.\-]+)(.*)$", text)
    if not match:
        raise ValueError(f"no library name in {text!r}")
    name = match.group(1).lower().replace("_", "-")
    rule = "".join(match.group(2).split())
    return name, rule


def merge_requirements(existing, new):
    merged = {}
    for text in list(existing) + list(new):
        name, rule = split_requirement(text)
        merged[name] = rule
    return [name + merged[name] for name in sorted(merged)]
