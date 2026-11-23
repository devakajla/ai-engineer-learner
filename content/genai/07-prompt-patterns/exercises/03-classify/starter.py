# Given from the lesson. Do not change it.
def pick_label(reply, labels):
    cleaned = reply.strip().lower().strip(".")
    if cleaned in labels:
        return cleaned
    return "unknown"


# Your task:
def classify(client, text, labels):
    ...
