def total_latency(stages):
    return sum(max((ms for _, ms in group), default=0) for group in stages)


def critical_path(stages):
    path = []
    for group in stages:
        if group:
            path.append(max(group, key=lambda item: item[1]))
    return path


def latency_report(stages, budget_ms):
    total = total_latency(stages)
    path = critical_path(stages)
    biggest = max(path, key=lambda item: item[1])[0] if path else None
    return {"total_ms": total, "ok": total <= budget_ms, "over_by": max(0, total - budget_ms), "biggest": biggest}
