# Given from earlier exercises. Do not change these.
def format_sse(data, event=None):
    parts = []
    if event:
        parts.append("event: " + event)
    for line in data.split("\n"):
        parts.append("data: " + line)
    return "\n".join(parts) + "\n\n"


def chunk_text(chunk):
    if not chunk.choices:
        return ""
    text = chunk.choices[0].delta.content
    if text is None:
        return ""
    return text


# Your task:
def sse_safe(stream, event="token"):
    ...
