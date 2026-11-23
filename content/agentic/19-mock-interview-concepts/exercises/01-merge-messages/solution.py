def merge_messages(old, new):
    merged = list(old)
    position = {m["id"]: i for i, m in enumerate(merged) if m.get("id") is not None}
    for message in new:
        message_id = message.get("id")
        if message_id is not None and message_id in position:
            merged[position[message_id]] = message
        else:
            merged.append(message)
            if message_id is not None:
                position[message_id] = len(merged) - 1
    return merged
