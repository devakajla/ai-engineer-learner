# Given from earlier exercises. Do not change these.
def allowed(chunk, user):
    if chunk["tenant"] != user["tenant"]:
        return False
    groups = chunk.get("groups", [])
    if not groups:
        return True
    return any(group in user.get("groups", []) for group in groups)


# Your task:
def filter_hits(hits, user):
    ...
