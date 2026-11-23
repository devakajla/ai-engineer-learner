from datetime import date


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
