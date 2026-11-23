from itertools import islice


def parse(lines):
    for line in lines:
        if not line.strip():
            continue
        ts, level, msg = line.split(" ", 2)
        yield {"ts": ts, "level": level, "msg": msg}


def filter_level(records, level):
    return (r for r in records if r["level"] == level)


def messages(records):
    for r in records:
        yield r["msg"]


def first_errors(lines, n):
    return list(islice(messages(filter_level(parse(lines), "ERROR")), n))
