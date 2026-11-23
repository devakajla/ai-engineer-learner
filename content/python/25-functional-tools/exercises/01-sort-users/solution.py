def by_age_desc_name(users):
    return sorted(users, key=lambda u: (-u["age"], u["name"].lower()))


def oldest_active(users):
    return max((u for u in users if u["active"]), key=lambda u: u["age"], default=None)


def has_minor(users):
    return any(u["age"] < 18 for u in users)


def names_by_id(ids, names):
    return dict(zip(ids, names, strict=True))
