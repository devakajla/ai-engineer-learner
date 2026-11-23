def check_budget(used, limits):
    names = [
        ("max_steps", "steps"),
        ("max_tokens", "tokens"),
        ("max_cost", "cost"),
        ("max_seconds", "seconds"),
    ]
    for limit_name, used_name in names:
        if limit_name in limits and used.get(used_name, 0) >= limits[limit_name]:
            return limit_name
    return None
