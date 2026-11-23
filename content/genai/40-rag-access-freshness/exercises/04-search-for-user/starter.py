from datetime import date


# Given from earlier exercises. Do not change these.
def allowed(chunk, user):
    if chunk["tenant"] != user["tenant"]:
        return False
    groups = chunk.get("groups", [])
    if not groups:
        return True
    return any(group in user.get("groups", []) for group in groups)


def filter_hits(hits, user):
    return [hit for hit in hits if allowed(hit, user)]


def drop_stale(hits, today, max_age_days):
    today_date = date.fromisoformat(today)
    fresh = []
    for hit in hits:
        updated = hit.get("updated")
        if updated is None:
            fresh.append(hit)
            continue
        age = (today_date - date.fromisoformat(updated)).days
        if age <= max_age_days:
            fresh.append(hit)
    return fresh


# Your task:
def search_for_user(retrieve, user, question, k=3, today=None, max_age_days=None, overfetch=5):
    ...
