PATTERNS = {
    "override": ["ignore previous", "ignore all previous", "disregard"],
    "secret": ["system prompt", "api key", "password"],
    "hidden": ["do not tell the user", "don't tell the user"],
    "exfil": ["send it to", "send this to", "upload it to"],
}


def scan_tool_output(text):
    ...


def quarantine(name, text, max_chars=300):
    ...
