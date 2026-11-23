# Given. Do not change this.
PATTERNS = [
    "ignore previous instructions",
    "ignore all previous instructions",
    "ignore your instructions",
    "disregard the above",
    "you are now",
    "reveal your system prompt",
]


def find_injection(text):
    lowered = text.lower()
    return [p for p in PATTERNS if p in lowered]
