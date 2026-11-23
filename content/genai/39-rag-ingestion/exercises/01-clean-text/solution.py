def clean_text(raw):
    text = raw.replace("\r\n", "\n").replace("-\n", "")
    lines = []
    for line in text.split("\n"):
        line = " ".join(line.split())
        if line.isdigit():
            continue
        lines.append(line)
    result = "\n".join(lines)
    while "\n\n\n" in result:
        result = result.replace("\n\n\n", "\n\n")
    return result.strip()
