OPERATORS = ["==", "!=", ">=", "<=", ">", "<"]


def parse_version(text):
    parts = text.strip().split(".")
    try:
        return tuple(int(part) for part in parts)
    except ValueError:
        raise ValueError(f"not a version: {text!r}") from None


def _pad(a, b):
    size = max(len(a), len(b))
    return a + (0,) * (size - len(a)), b + (0,) * (size - len(b))


def _check(version, condition):
    for op in OPERATORS:
        if condition.startswith(op):
            wanted = parse_version(condition[len(op):])
            left, right = _pad(version, wanted)
            return {
                "==": left == right,
                "!=": left != right,
                ">=": left >= right,
                "<=": left <= right,
                ">": left > right,
                "<": left < right,
            }[op]
    raise ValueError(f"unknown operator in {condition!r}")


def satisfies(version, rule):
    current = parse_version(version)
    conditions = [c.strip() for c in rule.split(",") if c.strip()]
    return all(_check(current, c) for c in conditions)
