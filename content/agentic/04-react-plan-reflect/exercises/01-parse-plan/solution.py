def parse_plan(text):
    steps = []
    for line in text.splitlines():
        line = line.strip()
        i = 0
        while i < len(line) and line[i].isdigit():
            i += 1
        if i == 0 or line[i:i + 1] not in (".", ")"):
            continue
        step = line[i + 1:].strip()
        if step:
            steps.append(step)
    return steps
