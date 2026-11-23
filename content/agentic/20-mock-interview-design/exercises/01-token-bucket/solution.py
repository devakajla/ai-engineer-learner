def new_bucket(rate_per_second, capacity, now=0.0):
    return {"rate": rate_per_second, "capacity": capacity, "tokens": float(capacity), "last": now}


def allow(bucket, now, cost=1):
    elapsed = max(0.0, now - bucket["last"])
    bucket["tokens"] = min(bucket["capacity"], bucket["tokens"] + elapsed * bucket["rate"])
    bucket["last"] = now
    if bucket["tokens"] >= cost:
        bucket["tokens"] -= cost
        return True
    return False
