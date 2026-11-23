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
