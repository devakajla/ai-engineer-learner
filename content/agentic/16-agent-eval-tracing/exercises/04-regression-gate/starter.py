# Given from earlier exercises. Do not change these.
def pass_rate(results):
    if not results:
        return 0.0
    return round(sum(1 for r in results if r["passed"]) / len(results), 2)


# Your task:
def find_regressions(baseline, new):
    ...


def gate(baseline, new, max_drop=0.05, max_token_growth=0.2):
    ...
