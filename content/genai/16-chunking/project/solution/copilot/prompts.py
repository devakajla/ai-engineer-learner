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
}


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
