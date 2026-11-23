def allow_request(timestamps, now, limit, window):
    recent = [t for t in timestamps if now - window < t <= now]
    if len(recent) < limit:
        return {"allowed": True, "timestamps": recent + [now], "retry_after": 0}
    retry_after = recent[0] + window - now
    return {"allowed": False, "timestamps": recent, "retry_after": retry_after}
