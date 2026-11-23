# Given from earlier exercises. Do not change these.
def check_input(text, max_chars=2000, banned=None):
    if not text.strip():
        return {"ok": False, "reason": "empty"}
    if len(text) > max_chars:
        return {"ok": False, "reason": "too long"}
    lowered = text.lower()
    for phrase in banned or []:
        if phrase.lower() in lowered:
            return {"ok": False, "reason": "banned phrase: " + phrase}
    return {"ok": True, "reason": ""}


def redact_pii(text):
    words = text.split(" ")
    result = []
    for word in words:
        core = word.rstrip(".,;:!?")
        tail = word[len(core):]
        at = core.find("@")
        digits = [char for char in core if char.isdigit()]
        only_phone_chars = all(char.isdigit() or char in "+-" for char in core)
        if at > 0 and "." in core[at + 1 :] and not core.endswith("."):
            result.append("[EMAIL]" + tail)
        elif only_phone_chars and len(digits) >= 10:
            result.append("[PHONE]" + tail)
        else:
            result.append(word)
    return " ".join(result)


REFUSAL = "Sorry, I can't help with that request."


# Your task:
def guarded_answer(client, text, system, max_chars=2000, banned=None):
    ...
