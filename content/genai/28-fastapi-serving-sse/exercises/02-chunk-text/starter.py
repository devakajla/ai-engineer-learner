# Given from earlier exercises. Do not change these.
def format_sse(data, event=None):
    parts = []
    if event:
        parts.append("event: " + event)
    for line in data.split("\n"):
        parts.append("data: " + line)
    return "\n".join(parts) + "\n\n"


# Your task:
def chunk_text(chunk):
    ...
