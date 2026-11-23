PATTERNS = {
    "override": ["ignore previous", "ignore all previous", "disregard"],
    "secret": ["system prompt", "api key", "password"],
    "hidden": ["do not tell the user", "don't tell the user"],
    "exfil": ["send it to", "send this to", "upload it to"],
}


def scan_tool_output(text):
    lower = text.lower()
    return sorted(label for label, phrases in PATTERNS.items() if any(p in lower for p in phrases))


def quarantine(name, text, max_chars=300):
    flags = scan_tool_output(text)
    body = text if len(text) <= max_chars else text[:max_chars] + "...[cut]"
    body = body.replace("</tool_output>", "[tag removed]")
    wrapped = f'<tool_output name="{name}" trust="untrusted">\n{body}\n</tool_output>'
    return {"text": wrapped, "flags": flags}
