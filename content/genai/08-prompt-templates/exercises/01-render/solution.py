def render(template, values):
    try:
        return template.format(**values)
    except KeyError as e:
        raise ValueError(f"missing variable: {e.args[0]}")
