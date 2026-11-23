# Given from earlier exercises. Do not change these.
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


def wrap_untrusted(text, tag="document"):
    clean = text.replace(f"<{tag}>", "").replace(f"</{tag}>", "")
    return {"text": f"<{tag}>\n{clean}\n</{tag}>", "flags": find_injection(text)}
