# Given from earlier exercises. Do not change these.
def pass_rate(results):
    if not results:
        return 0.0
    return round(sum(1 for r in results if r["passed"]) / len(results), 2)


# Your task:
def find_regressions(baseline, new):
    before = {r["id"]: r["passed"] for r in baseline}
    return [r["id"] for r in new if before.get(r["id"]) and not r["passed"]]


def gate(baseline, new, max_drop=0.05, max_token_growth=0.2):
    reasons = []
    drop = round(pass_rate(baseline) - pass_rate(new), 2)
    if drop > max_drop:
        reasons.append(f"pass rate fell by {drop}")
    regressions = find_regressions(baseline, new)
    if regressions:
        reasons.append("regressions: " + ", ".join(regressions))
    old_tokens = sum(r["tokens"] for r in baseline)
    new_tokens = sum(r["tokens"] for r in new)
    if old_tokens and (new_tokens - old_tokens) / old_tokens > max_token_growth:
        reasons.append(f"token use grew by {round(100 * (new_tokens - old_tokens) / old_tokens)}%")
    return {"ok": not reasons, "reasons": reasons}
