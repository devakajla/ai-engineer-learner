# Given from the earlier exercises. Do not change them.
def render(template, values):
    try:
        return template.format(**values)
    except KeyError as e:
        raise ValueError(f"missing variable: {e.args[0]}")


def get_prompt(registry, name, version=None):
    versions = registry[name]
    if version is not None:
        return versions[version]
    best_name = None
    best_number = -1
    for version_name in versions:
        number = int(version_name[1:])
        if number > best_number:
            best_name = version_name
            best_number = number
    return versions[best_name]


# Your task:
def render_prompt(registry, name, values, version=None):
    ...
