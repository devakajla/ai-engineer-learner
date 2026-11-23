def parse(lines):
    return [dict(zip(["ts", "level", "msg"], l.split(" ", 2))) for l in lines if l]


def filter_level(records, level):
    return [r for r in records if r["level"] == level]


def messages(records):
    return [r["msg"] for r in records]


def first_errors(lines, n):
    return messages(filter_level(parse(lines), "ERROR"))[:n]
