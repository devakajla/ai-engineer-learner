def add_section(sections, heading, lines):
    text = "\n".join(lines).strip()
    if text:
        sections.append({"heading": heading, "text": text})


def split_markdown(md):
    sections = []
    heading = ""
    lines = []
    in_fence = False
    for line in md.splitlines():
        if line.startswith("```"):
            in_fence = not in_fence
        stripped = line.lstrip("#")
        level = len(line) - len(stripped)
        is_heading = not in_fence and 1 <= level <= 6 and stripped.startswith(" ")
        if is_heading:
            add_section(sections, heading, lines)
            heading = stripped.strip()
            lines = []
        else:
            lines.append(line)
    add_section(sections, heading, lines)
    return sections
