from string import Formatter


def placeholders(template):
    found = []
    for text, name, spec, conversion in Formatter().parse(template):
        if name is not None and name not in found:
            found.append(name)
    return found
