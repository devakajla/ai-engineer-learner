def contextualize(text, title="", heading=""):
    parts = [part for part in (title, heading) if part]
    if not parts:
        return text
    return " > ".join(parts) + "\n\n" + text
