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
