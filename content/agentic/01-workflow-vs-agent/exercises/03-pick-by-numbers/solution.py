def rank(candidate):
    return (candidate["cost"], candidate["seconds"], candidate["name"])


def pick_by_numbers(candidates, min_success, max_cost, max_seconds):
    good = []
    for candidate in candidates:
        if (
            candidate["success"] >= min_success
            and candidate["cost"] <= max_cost
            and candidate["seconds"] <= max_seconds
        ):
            good.append(candidate)
    if not good:
        return None
    return min(good, key=rank)["name"]
