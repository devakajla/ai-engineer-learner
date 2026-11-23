def _pairs(d, prefix, sep):
    for key, value in d.items():
        full = f"{prefix}{sep}{key}" if prefix else key
        if isinstance(value, dict):
            yield from _pairs(value, full, sep)
        else:
            yield full, value


def flatten(d, sep="."):
    return dict(_pairs(d, "", sep))


def unflatten(flat, sep="."):
    root: dict = {}
    for key, value in flat.items():
        parts = key.split(sep)
        node = root
        for part in parts[:-1]:
            nxt = node.setdefault(part, {})
            if not isinstance(nxt, dict):
                raise ValueError(f"conflict at {part!r} in {key!r}")
            node = nxt
        if parts[-1] in node and isinstance(node[parts[-1]], dict):
            raise ValueError(f"conflict at {key!r}")
        node[parts[-1]] = value
    return root
